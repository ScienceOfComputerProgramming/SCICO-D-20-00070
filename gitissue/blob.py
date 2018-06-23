import hashlib
import os
import zlib

from git import Blob

from gitissue import IssueRepo
from gitissue import tools

__all__ = ('IssueBlob',)


class IssueBlob(Blob):

    def __init__(self, content, mode=None, path=None):
        self.content = content
        self.byte_content = content.encode()
        sha = hashlib.sha1(content.encode())
        self.repo = IssueRepo()
        self.binsha = sha.digest()
        super(IssueBlob, self).__init__(self.repo, self.binsha)

    def __get_location(self):
        # get the first two items in the sha for a folder
        folder = self.repo.issue_objects_dir + '/' + str(self.hexsha)[:2]
        # use the remainder of the string as a filename
        filename = folder + '/' + str(self.hexsha)[2:]
        return folder, filename

    def data_write(self):
        folder, filename = self.__get_location()
        if not os.path.exists(folder):
            os.makedirs(folder)
        f = open(filename, 'wb')
        f.write(zlib.compress(self.byte_content))
        f.close()

    # @property
    # def get_content(self):
    #     return self.content

    def data_stream(self):
        raise NotImplementedError

    def stream_data(self):
        raise NotImplementedError

