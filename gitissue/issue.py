import hashlib

from git import Object

from gitissue.functions import serialize, deserialize
from gitissue.errors import RepoObjectExistsError

__all__ = ('Issue',)


class Issue(Object):

    type = 'issue'

    def __init__(self, data, repo, binsha):
        super(Issue, self).__init__(repo, binsha)
        if data is not None:
            self.data = data
            self.filepath = data['filepath']
            self.contents = data['contents']
        else:
            deserialize(self)

    def __lt__(self, other):
        return str(self.hexsha) < str(other.hexsha)

    @classmethod
    def create(cls, repo, data):
        sha = hashlib.sha1(str(data).encode())
        binsha = sha.digest()
        new_issue = cls(data, repo, binsha)
        try:
            serialize(new_issue)
        except RepoObjectExistsError:
            pass
        return new_issue
