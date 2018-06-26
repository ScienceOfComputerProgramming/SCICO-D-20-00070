import hashlib
import os

from git import Object

from gitissue.functions import serialize, deserialize, object_exists
from gitissue.errors import RepoObjectExistsError

__all__ = ('Issue',)


def get_new_issue_no(repo):
    number_file = repo.issue_dir + '/NUMBER'

    if not os.path.exists(number_file):
        f = open(number_file, 'w')
        f.write('0')
        f.close()

    f = open(number_file, 'r')
    last_number = int(f.read())
    f.close()

    new_number = last_number + 1
    f = open(number_file, 'w')
    f.write(str(new_number))
    f.close()

    return new_number


class Issue(Object):

    __slots__ = ('data', 'filepath', 'contents', 'number', 'size')

    type = 'issue'

    def __init__(self, repo, binsha, data=None):
        super(Issue, self).__init__(repo, binsha)
        if not object_exists(self) and data is not None:
            self.number = get_new_issue_no(repo)
            data['number'] = self.number
            self.data = data
            self.filepath = data['filepath']
            self.contents = data['contents']
            serialize(self)
        else:
            deserialize(self)
            self.number = self.data['number']
            self.filepath = self.data['filepath']
            self.contents = self.data['contents']

    def __lt__(self, other):
        return str(self.hexsha) < str(other.hexsha)

    @classmethod
    def create(cls, repo, data):
        sha = hashlib.sha1(str(data).encode())
        binsha = sha.digest()
        new_issue = cls(repo, binsha, data)
        return new_issue
