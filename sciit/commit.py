# -*- coding: utf-8 -*-
"""Module that contains the definition of the issue commit.

:@author: Nystrom Edwards
:Created: 24 June 2018
"""

import re
import hashlib

from git import util, Object, Commit
from git.util import hex_to_bin

from sciit import IssueTree, Issue
from sciit.functions import serialize, deserialize, object_exists
from sciit.regex import PLAIN, CSTYLE, ISSUE, get_file_object_pattern
from sciit.issue import find_issue_data_in_comment

__all__ = ('IssueCommit', 'find_issues_in_commit')


def find_issues_in_commit(repo, commit, pattern=None):
    """
    Find issues in files that were changed during a commit.

    Args:
        :(Repo) repo: The issue repository
        :(CommitTree) commit_tree: The tree object of a git commit
        :(list) pattern: a specified regex pattern to match

    Returns:
        :(list(Issues)) issues: a list of issues
    """

    def get_blobs(tree):
        """
        Gets all the blobs associated to a commit tree.

        Args:
            :(CommitTree) tree: The tree object of a git commit

        Returns:
            :(dict(Blobs)) blobs: a dictionary of blobs
        """
        blobs = {}
        blobs.update({x.path: x for x in tree.blobs})
        for tree in tree.trees:
            blobs.update(get_blobs(tree))
        return blobs

    issues = []
    files_changed = commit.stats.files.keys()
    blobs = get_blobs(commit.tree)

    for change in files_changed:
        # handles renaming and deleted files they wont exist
        if change not in blobs:
            continue

        # get file extension and set pattern
        if pattern is None:
            search = get_file_object_pattern(blobs[change])
        else:
            search = pattern
        if search is False:
            continue

        try:
            # read the data contained in that file
            object_contents = blobs[change].data_stream.read().decode('utf-8')
        except (UnicodeDecodeError, AttributeError):
            continue

        # search for comment blocks in file based on file type
        # filter comment blocks that contain issues
        comments = re.findall(search, object_contents)
        comments = [x for x in comments if re.search(ISSUE.ID, x) is not None]
        for comment in comments:
            if search == PLAIN:
                comment = re.sub(r'^\s*#', '', comment, flags=re.M)
            if search == CSTYLE:
                comment = re.sub(r'^\s*\*', '', comment, flags=re.M)
            issue_data = find_issue_data_in_comment(comment)
            if issue_data:
                issue_data['filepath'] = change
                issue = Issue.create(repo, issue_data)
                issues.append(issue)

    # bring forward the open issues that had no
    # changes made to them from all available parents
    for parent in commit.parents:
        icommit = IssueCommit(repo, parent.hexsha)
        blah = [x for x in icommit.issuetree.issues
                if x.filepath not in files_changed]
        issues.extend(blah)

    return issues


class IssueCommit(Object):
    """IssueCommit objects represent a git commit object linked to an
    IssueTree.

    :note:
        When creating a tree if the object already exists the
        existing object is returned
    """
    __slots__ = ('data', 'commit', 'size', 'issuetree')

    type = 'issuecommit'
    """ The base type of this issue repository object
    """

    def __init__(self, repo, sha, issuetree=None):
        """Initialize a newly instanced IssueCommiy

        Args:
            :(Repo) repo: is the Repo we are located in
            :(bytes/str) sha: 20 byte binary sha1 or 40 character hexidecimal sha1
            :(IssueTree) issuetree:
                the issue tree that contains all the issue contents for this commit

        :note:
            The object may be deserialised from the file system when instatiated
            or serialized to the file system when the object is created from a factory
        """
        if len(sha) > 20:
            sha = hex_to_bin(sha)
        super(IssueCommit, self).__init__(repo, sha)
        self.commit = Commit(repo, sha)
        """ The git commit object that this issue commit is referencing
        see `GitPython.Commit <https://gitpython.readthedocs.io/en/stable/reference.html#module-git.objects.commit/>`_.
        """
        if not object_exists(self) and issuetree is not None:
            self.data = {'commit': self.commit.hexsha,
                         'itree': issuetree.hexsha
                         }
            """Dictionary containing issue commit data that is easily
            serializable/deserializable

                :data['commit']: the sha value of the git commit
                :data['itree']: the sha value of the issue tree
            """
            self.issuetree = issuetree
            """The :py:class:`IssueTree` that is attached to this issue commit
            """
            serialize(self)
        else:
            deserialize(self)
            self.issuetree = IssueTree(repo, self.data['itree'])

    @property
    def children(self):
        """
        The list of children that this commit has.
        """
        children = []
        rev_list = self.repo.git.execute(
            ['git', 'rev-list', '--all', '--children'])
        pattern = re.compile(r'(?:' + self.hexsha + ')(.*)')
        child_shas = pattern.findall(rev_list)[0]
        child_shas = child_shas.strip(' ').split(' ')
        if child_shas[0] != '':
            for child in child_shas:
                children.append(Commit(self.repo, hex_to_bin(child)))
        return children

    @property
    def open_issues(self):
        """The number of issues that are open in this particular commit
        as the length of the issues in the issue tree
        """
        return len(self.issuetree.issues)

    @classmethod
    def create(cls, repo, commit, issuetree):
        """Factory method that creates an IssueCommit with its issuetree
        or return the IssueCommit from the FileSystem

        Args:
            :(Repo) repo: is the Repo we are located in
            :(Commit) commit: is the git commit that we are linking to
            :(IssueTree) issuetree:
                the issue tree that contains all the issue contents for this commit
        """
        new_commit = cls(repo, commit.binsha, issuetree)
        return new_commit
