# -*- coding: utf-8 -*-
"""
Functions for interfacing with repository objects on the file system.
"""

import os
import pathspec


def write_last_issue_commit_sha(issue_dir, sha):
    last_issue_commit_file_path = issue_dir + '/LAST'
    with open(last_issue_commit_file_path, 'w') as last_issue_commit_file:
        last_issue_commit_file.write(sha)


def get_last_issue_commit_sha(issue_dir):
    last_issue_commit_file_path = issue_dir + '/LAST'
    with open(last_issue_commit_file_path, 'r') as last_issue_commit_file:
        return last_issue_commit_file.read()


def get_sciit_ignore_path_spec(repo):
    sciit_ignore_file_path = repo.working_dir + '/.sciitignore'
    if os.path.exists(sciit_ignore_file_path):
        with open(sciit_ignore_file_path, 'r') as file_handle:
            file_data = file_handle.read().splitlines()
            return pathspec.PathSpec.from_lines('gitignore', file_data)
    else:
        return None
