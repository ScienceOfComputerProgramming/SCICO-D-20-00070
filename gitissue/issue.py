import hashlib
import os
import zlib

from stat import S_IREAD

from git import Object

from gitissue import IssueRepo
from gitissue import tools

__all__ = ('Issue',)


class Issue(Object):

    type = 'issue'

    def __init__(self, data, repo, binsha):
        super(Issue, self).__init__(repo, binsha)
        if data is not None:
            self.data = data

    def __get_location(self):
        # get the first two items in the sha for a folder
        folder = self.repo.issue_objects_dir + '/' + str(self.hexsha)[:2]
        # use the remainder of the string as a filename
        filename = folder + '/' + str(self.hexsha)[2:]
        return folder, filename

    def __serialize(self):
        folder, filename = self.__get_location()
        if not os.path.exists(folder):
            os.makedirs(folder)

        # make the file, write compressed data, make read only
        f = open(filename, 'wb')
        f.write(zlib.compress(self.data.encode()))
        os.chmod(filename, S_IREAD)
        f.close()

        # get the size of the file on the system
        stats = os.stat(filename)
        self.size = stats.st_size
        return self

    def __deserialize(self):
        raise NotImplementedError

    @classmethod
    def create(cls, data):
        repo = IssueRepo()
        sha = hashlib.sha1(data.encode())
        binsha = sha.digest()
        new_issue = cls(data, repo, binsha)
        new_issue.__serialize()
        return new_issue
