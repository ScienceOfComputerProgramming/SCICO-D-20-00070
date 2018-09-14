# -*- coding: utf-8 -*-
"""Module that contains the functions needed to interface with the objects on
the file system.

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


def get_location(obj):
    """
    Args:
        :(object) obj: The repositiory object (IssueCommit, IssueTree, Issues)

    Returns:
        :(str,str)(folder, filename): the location of the file and folder \
        of any repository object (IssueCommit, IssueTree, Issues)

    """
    # get the first two items in the sha for a folder
    folder = obj.repo.issue_objects_dir + '/' + str(obj.hexsha)[:2]
    # use the remainder of the string as a filename
    filename = folder + '/' + str(obj.hexsha)[2:]
    return folder, filename


def get_type_from_sha(repo, sha):
    """Get object type from the raw sha of any issue object

    Args:
        :(Repo) repo: The repositiory where the sha exists
        :(str) sha: representing the sha of the object
    """
    folder = repo.issue_objects_dir + '/' + sha[:2]
    filename = folder + '/' + sha[2:]

    if not os.path.exists(filename):
        raise RepoObjectDoesNotExistError(filename)

    f = open(filename, 'rb')
    contents = zlib.decompress(f.read()).decode()
    obj_type = contents.split(' ', 1)[0]
    f.close()
    return obj_type


def object_exists(obj):
    """
    Args:
        :(object) obj: The repositiory object (IssueCommit, IssueTree, Issues)

    Returns:
        :bool: True if the repository object (IssueCommit, IssueTree, Issues) \
        exits
    """
    location = get_location(obj)
    filename = location[1]
    return os.path.exists(filename)


def serialize(obj):
    """
    Takes the data of the object file that is JSON serializable (lists and dicts)
    and creates a compressed read-only JSON file at the filesystem location 
    specified by the object sha.

    Args:
        :(object) obj: The repositiory object (IssueCommit, IssueTree, Issues)

    Returns:
        :(object) obj: The repository object (IssueCommit, IssueTree, Issues)

    Raises:
        :RepoObjectExistsError: in the event the object exists (read-only)
    """
    folder, filename = get_location(obj)
    if not os.path.exists(folder):
        os.makedirs(folder)

    data_to_write = json.dumps(obj.data)
    # Add object type to serialize
    data_to_write = obj.type + ' ' + data_to_write

    if os.path.exists(filename):
        raise RepoObjectExistsError
    # make the file, write compressed data, make read only

    f = open(filename, 'wb')
    f.write(zlib.compress(data_to_write.encode()))
    os.chmod(filename, S_IREAD)
    f.close()

    # get the size of the file on the system
    stats = os.stat(filename)
    obj.size = stats.st_size
    return obj


def deserialize(obj):
    """
    Takes the data of the object file that is a compressed JSON file on 
    the filesystem who's location is specified by the object sha and adds
    the JSON serializable (lists and dicts) data to the repository object.

    Args:
        :(object) obj: The repositiory object (IssueCommit, IssueTree, Issues)

    Returns:
        :(object) obj: The repository object (IssueCommit, IssueTree, Issues)

    Raises:
        :RepoObjectDoesNotExistError: in the event the object does not exist
    """
    location = get_location(obj)
    filename = location[1]
    if not os.path.exists(filename):
        raise RepoObjectDoesNotExistError(filename)
    f = open(filename, 'rb')
    contents = zlib.decompress(f.read()).decode()
    f.close()

    # remove the object type on deserialize
    contents = contents.split(' ', 1)[1]
    contents = json.loads(contents)
    obj.data = contents
    # get the size of the file on the system
    stats = os.stat(filename)
    obj.size = stats.st_size
    return obj


def cache_history(issue_dir, history):
    """Takes the issue history from the repo and saves all its issues 
    to a file containing the history of all issues ever created
    that were tracked.

    Args:
        :(str) issue_dir: the directory to store the issue *repo.issue_dir*
        :dict(dict) history: the history dictionary with all the issue \
        information
    """
    history_file = issue_dir + '/HISTORY'

    # convert item paths to sets
    for item in history.values():
        item['participants'] = list(item['participants'])
        item['in_branches'] = list(item['in_branches'])
        item['open_in'] = list(item['open_in'])

    now = datetime.now().strftime('%a %b %d %H:%M:%S %Y %z')
    f = open(history_file, 'w')
    f.write(now + '\n')
    f.write(json.dumps(history, indent=4))
    f.close()


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
