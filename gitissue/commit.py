import hashlib

from git import util
from git import Object
from git import Commit
from git.util import hex_to_bin

from gitissue import IssueTree
from gitissue.functions import serialize, deserialize, object_exists
from gitissue.errors import RepoObjectExistsError

__all__ = ("IssueCommit")


class IssueCommit(Object):
    """IssueTree objects represent an ordered list of Issues.
    """
    __slots__ = ('data', 'commit', 'size', 'issuetree')

    type = "issuecommit"

    def __init__(self, repo, sha, issuetree=None):
        if len(sha) > 20:
            sha = hex_to_bin(sha)
        super(IssueCommit, self).__init__(repo, sha)
        self.commit = Commit(repo, sha)
        if not object_exists(self) and issuetree is not None:
            self.data = {'commit_hexsha': self.commit.hexsha,
                         'issuetree_hexsha': issuetree.hexsha
                         }
            self.issuetree = issuetree
            serialize(self)
        else:
            deserialize(self)
            self.issuetree = IssueTree(repo, self.data['issuetree_sha'])

    @classmethod
    def create(cls, repo, commit, issuetree):
        new_commit = cls(repo, commit.binsha, issuetree)
        return new_commit
