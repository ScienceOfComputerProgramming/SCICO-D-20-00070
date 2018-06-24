import os
import zlib

from stat import S_IREAD
from gitissue.errors import RepoObjectExistsError


def get_location(object):
    # get the first two items in the sha for a folder
    folder = object.repo.issue_objects_dir + '/' + str(object.hexsha)[:2]
    # use the remainder of the string as a filename
    filename = folder + '/' + str(object.hexsha)[2:]
    return folder, filename


def serialize(object):
    folder, filename = get_location(object)
    if not os.path.exists(folder):
        os.makedirs(folder)

    data_to_write = str(object.data)

    # make the file, write compressed data, make read only

    if os.path.exists(filename):
        raise RepoObjectExistsError

    f = open(filename, 'wb')
    f.write(zlib.compress(data_to_write.encode()))
    os.chmod(filename, S_IREAD)
    f.close()

    # get the size of the file on the system
    stats = os.stat(filename)
    object.size = stats.st_size
    return object


def deserialize(object):
    raise NotImplementedError
