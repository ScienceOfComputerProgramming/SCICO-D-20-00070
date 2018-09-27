# -*- coding: utf-8 -*-
"""
Functions for interfacing with repository objects on the file system.
"""

import os
import zlib
import json
import pathspec
from datetime import datetime
from stat import S_IREAD
from sciit.errors import RepoObjectExistsError, RepoObjectDoesNotExistError


def get_repository_object_path(repo, hexsha):
    return repo.issue_objects_dir + '/' + str(hexsha)[:2] + '/' + str(hexsha)[2:]


def repository_object_exists(repo, hexsha):
    return os.path.exists(get_repository_object_path(repo, hexsha))


def get_repository_object_type_from_sha(repo, hexsha):

    path = get_repository_object_path(repo, hexsha)

    if not repository_object_exists(repo, hexsha):
        raise RepoObjectDoesNotExistError(path)

    with open(path, 'rb') as f:
        contents = zlib.decompress(f.read()).decode()
        obj_type = contents.split(' ', 1)[0]
        return obj_type


def serialize_repository_object_as_json(repo, hexsha, repo_obj_type, data):
    path = get_repository_object_path(repo, hexsha)
    if os.path.exists(path):
        raise RepoObjectExistsError

    parent = os.path.split(path)[0]
    if not os.path.exists(parent):
        os.makedirs(parent)

    data_to_write = json.dumps(data)
    data_to_write = repo_obj_type.__name__ + ' ' + data_to_write

    with open(path, 'wb') as f:
        f.write(zlib.compress(data_to_write.encode()))
        os.chmod(path, S_IREAD)


def get_repository_object_size(repo, hexsha):
    path = get_repository_object_path(repo, hexsha)
    return os.stat(path).st_size


def deserialize_repository_object_from_json(repo, hexsha):
    path = get_repository_object_path(repo, hexsha)

    if not os.path.exists(path):
        raise RepoObjectDoesNotExistError(path)

    with open(path, 'rb') as f:
        contents = zlib.decompress(f.read()).decode()
        return json.loads(contents.split(' ', 1)[1]), os.stat(path).st_size


def cache_history(issue_dir, history):
    history_file = issue_dir + '/HISTORY'

    json_history = {
        id: {
            'title': issue.title,
            'description': issue.description,
            'participants': list(issue.participants),
            'in_branches': list(issue.in_branches),
            'open_in': list(issue.open_in),
            # TODO...
        }
        for id, issue in history.items()
    }

    now = datetime.now().strftime('%a %b %d %H:%M:%S %Y %z')
    with open(history_file, 'w') as f:
        f.write(now + '\n')
        f.write(json.dumps(json_history, indent=4))


def write_last_issue_commit_sha(issue_dir, sha):
    last_issue_commit_file_path = issue_dir + '/LAST'
    with open(last_issue_commit_file_path, 'w') as f:
        f.write(sha)


def get_last_issue_commit_sha(issue_dir):
    last_issue_commit_file_path = issue_dir + '/LAST'
    with open(last_issue_commit_file_path, 'r') as f:
        return f.read()


def get_sciit_ignore_path_spec(repo):
    sciit_ignore_file_path = repo.working_dir + '/.sciitignore'
    if os.path.exists(sciit_ignore_file_path):
        with open(sciit_ignore_file_path, 'r') as fh:
            fh = fh.read().splitlines()
            return pathspec.PathSpec.from_lines('gitignore', fh)
    else:
        return None
