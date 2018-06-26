import os
import zlib
import json

from stat import S_IREAD
from gitissue.errors import RepoObjectExistsError


def get_location(obj):
    # get the first two items in the sha for a folder
    folder = obj.repo.issue_objects_dir + '/' + str(obj.hexsha)[:2]
    # use the remainder of the string as a filename
    filename = folder + '/' + str(obj.hexsha)[2:]
    return folder, filename


def object_exists(obj):
    folder, filename = get_location(obj)
    return os.path.exists(filename)


def serialize(obj):
    folder, filename = get_location(obj)
    if not os.path.exists(folder):
        os.makedirs(folder)

    data_to_write = json.dumps(obj.data)

    # make the file, write compressed data, make read only

    if os.path.exists(filename):
        raise RepoObjectExistsError

    f = open(filename, 'wb')
    f.write(zlib.compress(data_to_write.encode()))
    os.chmod(filename, S_IREAD)
    f.close()

    # get the size of the file on the system
    stats = os.stat(filename)
    obj.size = stats.st_size
    return obj


def deserialize(obj):
    folder, filename = get_location(obj)
    f = open(filename, 'rb')
    contents = zlib.decompress(f.read()).decode()
    f.close()
    contents = json.loads(contents)
    obj.data = contents
    return obj
