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
from gitissue.errors import RepoObjectExistsError, RepoObjectDoesNotExistError


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


"""
@issue cache issue history / export issue tracker
@description
    It may be much better to use a type of caching for issue history
    than saving the history tree intermitantly to disk. This can be some
    type of readable JSON file.
"""


def cache_history(repo):
    """Takes an issue repo and saves all its issues 
    to a file containing the history of all issues ever created
    that were tracked.

    Args:
        :(IssueRepo) repo: The repo to use to save issue history file.
    """
    raise NotImplementedError
