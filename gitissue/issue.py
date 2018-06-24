import hashlib

from git import Object

from gitissue.functions import *

__all__ = ('Issue',)


class Issue(Object):

    type = 'issue'

    def __init__(self, data, repo, binsha):
        super(Issue, self).__init__(repo, binsha)
        if data is not None:
            self.data = data
        else:
            deserialize(self)

    @classmethod
    def create(cls, repo, data):
        sha = hashlib.sha1(str(data).encode())
        binsha = sha.digest()
        new_issue = cls(data, repo, binsha)
        try:
            serialize(new_issue)
        except RepoObjectExists:
            pass
        return new_issue
