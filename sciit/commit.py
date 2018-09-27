# -*- coding: utf-8 -*-
"""
Module that contains the definition of the issue commit.

:@author: Nystrom Edwards
:Created: 24 June 2018
"""

import re

from git import Object, Commit
from git.util import hex_to_bin

from sciit import IssueTree, Issue
from sciit.functions import serialize_repository_object_as_json, deserialize_repository_object_from_json, repository_object_exists
from sciit.regex import PLAIN, CSTYLE, ISSUE, get_file_object_pattern


__all__ = ('IssueCommit', 'find_issues_in_commit')


def get_blobs(tree):
    """
    Gets all the blobs associated to a commit tree.

    Args:
        :(CommitTree) tree: The tree object of a git commit

    Returns:
        :(dict(Blobs)) blobs: a dictionary of blobs
    """
    blobs = dict()
    blobs.update({x.path: x for x in tree.blobs})
    for tree in tree.trees:
        blobs.update(get_blobs(tree))
    return blobs


def find_issue_data_in_comment(comment):
    """
    Finds the relevant issue data in block comments made by the user in source code. Only if an issue is specified does
    the function continue to extract other issue data.

    Args:
        :(str) comment: raw string representation of \
        the block comment

    Returns:
        :(dict) data: contains all the relevant issue data
    """
    data = {}

    def update_issue_data_dict_with_value_from_comment(regex, key):
        value = re.findall(regex, comment)
        if len(value) > 0:
            data[key] = value[0]

    update_issue_data_dict_with_value_from_comment(ISSUE.ID, 'id')

    if 'id' in data:
        update_issue_data_dict_with_value_from_comment(ISSUE.TITLE, 'title')
        update_issue_data_dict_with_value_from_comment(ISSUE.DESCRIPTION, 'description')
        update_issue_data_dict_with_value_from_comment(ISSUE.ASSIGNEES, 'assignees')
        update_issue_data_dict_with_value_from_comment(ISSUE.LABEL, 'label')
        update_issue_data_dict_with_value_from_comment(ISSUE.DUE_DATE, 'due_date')
        update_issue_data_dict_with_value_from_comment(ISSUE.PRIORITY, 'priority')
        update_issue_data_dict_with_value_from_comment(ISSUE.WEIGHT, 'weight')

    return data


def find_issues_data_in_blob_content(search, object_contents):

    comments = re.findall(search, object_contents)
    comments_with_issues = [x for x in comments if re.search(ISSUE.ID, x) is not None]

    issues = list()

    for comment in comments_with_issues:
        if search == PLAIN:
            comment = re.sub(r'^\s*#', '', comment, flags=re.M)
        if search == CSTYLE:
            comment = re.sub(r'^\s*\*', '', comment, flags=re.M)
        issue = find_issue_data_in_comment(comment)
        if issue:
            issues.append(issue)

    return issues


def find_issues_in_commit(repo, commit, comment_pattern=None, ignored_files=None):
    """
    Find issues in files that were changed during a commit.

    Args:
        :(Repo) repo: The issue repository
        :(CommitTree) commit_tree: The tree object of a git commit
        :(list) pattern: a specified regex pattern to match

    Returns:
        :(list(Issues)) issues: a list of issues
    """

    issues = list()
    files_changed = set(commit.stats.files.keys())
    blobs = get_blobs(commit.tree)

    # Exclude patterns from some file types if specified.
    if ignored_files:
        matches = set(ignored_files.match_files(files_changed))
        files_changed -= matches

    for file_changed in files_changed:
        # handles renaming and deleted files they won't exist
        if file_changed not in blobs:
            continue

        # get file extension and set pattern
        if not comment_pattern:
            comment_pattern = get_file_object_pattern(blobs[file_changed])

        if not comment_pattern:
            continue

        try:
            object_contents = blobs[file_changed].data_stream.read().decode('utf-8')
            blob_issues = find_issues_data_in_blob_content(comment_pattern, object_contents)

            for issue_data in blob_issues:
                issue_data['filepath'] = file_changed
                issue = Issue.create_from_data(repo, issue_data)
                issues.append(issue)

        except (UnicodeDecodeError, AttributeError):
            continue

    # Bring forward the open issues that had no changes made to them from all available parents.
    for parent in commit.parents:
        issue_commit = IssueCommit(repo, parent.hexsha)
        old_issues = [x for x in issue_commit.issue_tree.issues if x.filepath not in files_changed]
        issues.extend(old_issues)

    return issues


class IssueCommit(Object):
    """
    IssueCommit objects represent a git commit object linked to an IssueTree.

    :note:
        When creating a tree if the object already exists the existing object is returned.
    """
    __slots__ = ('data', 'commit', 'size', 'issue_tree', 'time_format')

    def __init__(self, repo, sha, issue_tree=None, time_format='%a %b %d %H:%M:%S %Y %z'):
        """
        Initialize a newly instanced IssueCommit

        Args:
            :(Repo) repo: is the Repo we are located in
            :(bytes/str) sha: 20 byte binary sha1 or 40 character hexidecimal sha1
            :(IssueTree) issue_tree:
                the issue tree that contains all the issue contents for this commit

        :note:
            The object may be de-serialised from the file system when instantiated or serialized to the file system when
            the object is created from a factory.
        """

        if len(sha) > 20:
            sha = hex_to_bin(sha)
        super(IssueCommit, self).__init__(repo, sha)
        self.commit = Commit(repo, sha)

        # The git commit object that this issue commit is referencing
        # see `GitPython.Commit <https://gitpython.readthedocs.io/en/stable/reference.html#module-git.objects.commit/>`.

        if not repository_object_exists(self.repo, self.hexsha) and issue_tree is not None:
            self.data = {'commit': self.commit.hexsha, 'issue_tree': issue_tree.hexsha}
            self.issue_tree = issue_tree
            serialize_repository_object_as_json(self.repo, self.hexsha, IssueCommit, self.data)
        else:
            self.data, self.size = deserialize_repository_object_from_json(self.repo, self.hexsha)
            self.issue_tree = IssueTree(repo, self.data['issue_tree'])

        self.time_format = time_format

    @property
    def children(self):
        children = list()

        rev_list = self.repo.git.execute(['git', 'rev-list', '--all', '--children'])
        pattern = re.compile(r'(?:' + self.hexsha + ')(.*)')
        child_shas = pattern.findall(rev_list)[0]
        child_shas = child_shas.strip(' ').split(' ')
        if child_shas[0] != '':
            for child in child_shas:
                children.append(Commit(self.repo, hex_to_bin(child)))
        return children

    @property
    def open_issues(self):
        """The number of issues that are open in this particular commit as the length of the issues in the issue tree
        """
        return len(self.issue_tree.issues)

    @property
    def author_name(self):
        return self.commit.author.name

    @property
    def date_string(self):
        return self.commit.authored_datetime.strftime(self.time_format)

    @classmethod
    def create(cls, repo, commit, issue_tree):
        """
        Factory method that creates an IssueCommit with its issuetree or return the IssueCommit from the FileSystem

        Args:
            :(Repo) repo: is the Repo we are located in
            :(Commit) commit: is the git commit that we are linking to
            :(IssueTree) issuetree:
                the issue tree that contains all the issue contents for this commit
        """
        new_commit = cls(repo, commit.binsha, issue_tree)
        return new_commit

