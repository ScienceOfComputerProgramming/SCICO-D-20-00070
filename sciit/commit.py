# -*- coding: utf-8 -*-

import re

from git import Object, Commit
from git.util import hex_to_bin, bin_to_hex

from sciit import Issue
from sciit.functions import serialize_repository_object_as_json, deserialize_repository_object_from_json, \
    repository_object_exists, get_repository_object_size
from sciit.regex import PLAIN, CSTYLE, ISSUE, get_file_object_pattern


__all__ = ('IssueCommit', 'find_issues_in_commit')


def get_blobs_from_commit_tree(tree):
    blobs = dict()
    blobs.update({x.path: x for x in tree.blobs})
    for tree in tree.trees:
        blobs.update(get_blobs_from_commit_tree(tree))
    return blobs


def find_issue_in_comment(comment:str):

    issue = dict()

    def update_issue_data_dict_with_value_from_comment(regex, key):
        value = re.findall(regex, comment)
        if len(value) > 0:
            issue[key] = value[0]

    update_issue_data_dict_with_value_from_comment(ISSUE.ID, 'id')

    if 'id' in issue:
        update_issue_data_dict_with_value_from_comment(ISSUE.TITLE, 'title')
        update_issue_data_dict_with_value_from_comment(ISSUE.DESCRIPTION, 'description')
        update_issue_data_dict_with_value_from_comment(ISSUE.ASSIGNEES, 'assignees')
        update_issue_data_dict_with_value_from_comment(ISSUE.LABEL, 'label')
        update_issue_data_dict_with_value_from_comment(ISSUE.DUE_DATE, 'due_date')
        update_issue_data_dict_with_value_from_comment(ISSUE.PRIORITY, 'priority')
        update_issue_data_dict_with_value_from_comment(ISSUE.WEIGHT, 'weight')

    return issue


def find_issues_in_blob(search, blob_content):

    comments = re.findall(search, blob_content)
    comments_with_issues = [x for x in comments if re.search(ISSUE.ID, x) is not None]

    issues = list()

    for comment in comments_with_issues:
        if search == PLAIN:
            comment = re.sub(r'^\s*#', '', comment, flags=re.M)
        if search == CSTYLE:
            comment = re.sub(r'^\s*\*', '', comment, flags=re.M)
        issue = find_issue_in_comment(comment)
        if issue:
            issues.append(issue)

    return issues


def read_in_blob_contents(blob):
    blob_contents = blob.data_stream.read()
    if type(blob_contents) == bytes:
        return blob_contents.decode("utf-8")
    else:
        return blob_contents


def _get_unchanged_issues_from_commit_parents(repo, commit, files_changed_in_commit):
    result = list()
    for parent in commit.parents:
        issue_commit = IssueCommit.create_from_hexsha(repo, parent.hexsha)
        old_issues = [x for x in issue_commit.issues if x.filepath not in files_changed_in_commit]
        result.extend(old_issues)
    return result


def find_issues_in_commit(repo, commit, comment_pattern=None, ignore_files=None):

    issues = list()

    files_changed_in_commit = set(commit.stats.files.keys())
    blobs = get_blobs_from_commit_tree(commit.tree)

    if ignore_files:
        files_changed_in_commit -= set(ignore_files.match_files(files_changed_in_commit))

    for file_changed in files_changed_in_commit:

        # Handles renamed and deleted files they won't exist.
        if file_changed not in blobs:
            continue

        blob = blobs[file_changed]

        if not comment_pattern:
            comment_pattern = get_file_object_pattern(blob)

        if not comment_pattern:
            continue

        blob_contents = read_in_blob_contents(blob)

        blob_issues = find_issues_in_blob(comment_pattern, blob_contents)

        for issue_data in blob_issues:
            issue_data['filepath'] = file_changed
            issue = Issue.create_from_data(repo, issue_data)
            issues.append(issue)

    issues.extend(_get_unchanged_issues_from_commit_parents(repo, commit, files_changed_in_commit))
    return issues


class IssueCommit(Object):

    __slots__ = ('data', 'commit', 'size', 'issues', 'time_format')

    def __init__(self, repo, sha, issues, size, time_format='%a %b %d %H:%M:%S %Y %z'):
        if type(time_format) == int:
            raise Exception()
        super(IssueCommit, self).__init__(repo, sha)
        self.issues = issues
        self.commit = Commit(repo, sha)
        self.size = size
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
        # TODO rename this
        return len(self.issues)

    @property
    def author_name(self):
        return self.commit.author.name

    @property
    def date_string(self):
        return self.commit.authored_datetime.strftime(self.time_format)

    @classmethod
    def create_from_commit_and_issues(cls, repo, commit, issues):

        if not repository_object_exists(repo, commit.hexsha):
            data = [{'id': issue.data['id'], 'hexsha': issue.hexsha} for issue in issues]
            serialize_repository_object_as_json(repo, commit.hexsha, IssueCommit, data)

        size = get_repository_object_size(repo, commit.hexsha)
        return cls(repo, commit.binsha, issues, size)

    @classmethod
    def create_from_hexsha(cls, repo, hexsha):
        binsha = hex_to_bin(hexsha)
        data, size = deserialize_repository_object_from_json(repo, hexsha)

        issues = list()
        for issue_data in data:
            issues.append(Issue.create_from_hexsha(repo, issue_data['hexsha']))

        return cls(repo, binsha, issues, size)

    @classmethod
    def create_from_binsha(cls, repo, binsha):
        hexsha = bin_to_hex(binsha).decode("utf")
        data, size = deserialize_repository_object_from_json(repo, hexsha)

        issues = list()
        for issue_data in data:
            issues.append(Issue.create_from_hexsha(repo, issue_data['hexsha']))

        return cls(repo, binsha, issues, size)

