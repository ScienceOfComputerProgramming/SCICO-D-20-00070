# -*- coding: utf-8 -*-

import re

from sciit import IssueSnapshot
from sciit.regex import PLAIN, CSTYLE, ISSUE, get_file_object_pattern


__all__ = 'find_issues_in_commit'


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

    update_issue_data_dict_with_value_from_comment(ISSUE.ID, 'issue_id')

    if 'issue_id' in issue:
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
        try:
            return blob_contents.decode("utf-8")
        except UnicodeDecodeError as e:
            return None
    else:
        return blob_contents


def find_issue_snapshots_in_commit_paths_that_changed(commit, comment_pattern=None, ignore_files=None):
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
        if blob_contents is None:
            continue
        blob_issues = find_issues_in_blob(comment_pattern, blob_contents)
        for issue_data in blob_issues:
            issue_data['filepath'] = file_changed
            issue = IssueSnapshot(commit, issue_data)
            issues.append(issue)

    return issues, files_changed_in_commit
