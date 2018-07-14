# -*- coding: utf-8 -*-
"""Module that contains the functions needed to interface with the objects on
the file system.

:@author: Nystrom Edwards

:Created: 24 June 2018
"""

import os
import zlib
import json

from stat import S_IREAD
from gitissue.errors import RepoObjectExistsError, RepoObjectDoesNotExistError, NoIssueHistoryError


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
        raise RepoObjectDoesNotExistError

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
        raise RepoObjectDoesNotExistError
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


def save_issue_history(itree):
    """Takes an issue tree and saves all its tracked issues 
    to a file containing the history of all issues ever created
    that were tracked. *Skips operation if tree empty*

    Args:
        :(IssueTree) itree: The tree to use to save new issues to full history file.
    """
    if itree.issues:
        history = itree.repo.issue_dir + '/HISTORY'

        # if first time create empty file
        if not os.path.exists(history):
            contents = []
        else:
            f = open(history, 'rb')
            contents = zlib.decompress(f.read()).decode()
            f.close()
            contents = json.loads(contents)

        new_contents = []
        for issue in itree.issues:
            new_issue = {}
            new_issue['id'] = issue.id
            new_issue['sha'] = issue.hexsha
            new_contents.append(new_issue)
        contents.extend(new_contents)

        # remove duplicate ids and sort by id
        contents = list({v['id']: v for v in contents}.values())
        contents = sorted(contents, key=lambda v: v['id'])

        data_to_write = json.dumps(contents)
        f = open(history, 'wb')
        f.write(zlib.compress(data_to_write.encode()))
        f.close()


def get_issue_history(repo):
    """Returns all tracked issues from a file containing 
    the history of all issues ever created that were tracked.

    Args:
        :(Repo) repo: The repo where the issue history is located

    Returns:
        :(list(dict)) contents: the id and sha of the issue

    Raises:
        :NoIssueHistoryError: *If no issues created*
    """
    history = repo.issue_dir + '/HISTORY'

    # if first time create empty file
    if not os.path.exists(history):
        raise NoIssueHistoryError
    else:
        f = open(history, 'rb')
        contents = zlib.decompress(f.read()).decode()
        f.close()
        contents = json.loads(contents)
        return contents
