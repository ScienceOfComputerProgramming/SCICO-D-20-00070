from git import Blob, Repo
import hashlib

__all__ = ('IssueBlob',)


class IssueBlob(Blob):

    def __init__(self, contents, mode=None, path=None):
        self.contents = contents
        sha = hashlib.sha1(contents)
        self.repo = Repo()
        self.binsha = sha.digest()
        super(IssueBlob, self).__init__(self.repo, self.binsha)

    def write_blob(self):
        filename = self.repo.git_dir + '/issue/objects/' + str(self.hexsha)
        f = open(filename, 'w')
        f.write(self.contents)
        f.close
