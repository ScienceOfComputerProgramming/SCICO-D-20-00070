import os
import stat
import shutil

from unittest.mock import MagicMock
from sciit import IssueSnapshot


def onerror(func, path, excp_info):
    os.chmod(path, stat.S_IWUSR)
    func(path)


def remove_existing_repo(path):
    if os.path.exists(path):
        shutil.rmtree(path, onerror=onerror)


def safe_create_repo_dir(path):
    remove_existing_repo(path)

    os.makedirs(path)
    os.makedirs(path + "/objects")


def create_mock_git_repository(path, heads, commits):
    mock_git_repository = MagicMock()
    mock_git_repository.git_dir = path + '/.git'
    mock_git_repository.working_dir = 'path'
    safe_create_repo_dir(path + '/.git')

    mock_git_repository.heads = list()
    for head in heads:
        mock_head = MagicMock()
        mock_head.name = head[0]
        mock_head.commit.hexsha = head[1]
        mock_git_repository.heads.append(mock_head)

    if len(heads) > 0:
        mock_git_repository.head.commit.hexsha = heads[0][1]
        mock_git_repository.iter_commits.return_value = commits

    return mock_git_repository


def create_mock_commit(hexsha, author_name, authored_datetime, parents=list()):
    mock_commit = MagicMock()
    mock_commit.hexsha = hexsha
    mock_commit.author.name = author_name
    mock_commit.authored_datetime = authored_datetime
    mock_commit.parents = parents
    return mock_commit


def create_mock_commit_with_issue_snapshots(hexsha, author_name, authored_datetime, issue_snapshot_data, parents=list()):
    mock_commit = create_mock_commit(hexsha, author_name, authored_datetime, parents)
    mock_issue_snapshots = [IssueSnapshot(mock_commit, d) for d in issue_snapshot_data]
    return mock_commit, mock_issue_snapshots


def create_mock_parents(child_commits):
    return [MagicMock(commit=commit) for commit in child_commits]


