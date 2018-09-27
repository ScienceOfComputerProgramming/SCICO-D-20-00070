# -*- coding: utf-8 -*-
"""
Functions to interface with repository objects on the file system.
:@author: Nystrom Edwards
:Created: 24 June 2018
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


def write_last_issue(issue_dir, sha):
    """Takes the sha of the last issuecommit built and saves it 
    to a file to be used after post-checkout and post-merge hooks
    to identify new issues to be built

    Args:
        :(str) issue_dir: the directory to store the issue *repo.issue_dir*
        :(str) sha: the commit sha to be saved
    """
    last_issue_file = issue_dir + '/LAST'
    f = open(last_issue_file, 'w')
    f.write(sha)
    f.close()


def get_last_issue(repo):
    """Returns the sha of the last issuecommit reference saved

    Args:
        :(IssueRepo) repo: the repository to look for
    """
    last_issue_file = repo.issue_dir + '/LAST'
    f = open(last_issue_file, 'r')
    sha = f.read()
    f.close()
    return sha


def get_sciit_ignore(repo):
    """Returns the contents of the sciit ignore file to use
    when making commits

    Args:
        :(IssueRepo) repo: the repository to look for

    Returns:
        :(PathSpec) spec: a gitignore spec of expressions
    """
    sciit_ignore_file = repo.working_dir + '/.sciitignore'
    if os.path.exists(sciit_ignore_file):
        with open(sciit_ignore_file, 'r') as fh:
            fh = fh.read().splitlines()
            spec = pathspec.PathSpec.from_lines('gitignore', fh)
        return spec
    else:
        return None
