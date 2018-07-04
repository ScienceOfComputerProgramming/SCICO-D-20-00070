import hashlib

from git import util
from git import Object
from git.util import hex_to_bin

from gitissue import Issue
from gitissue.functions import serialize, deserialize, object_exists
from gitissue.errors import RepoObjectExistsError

__all__ = ("IssueTree")


class IssueTree(Object):
    """IssueTree objects represent an ordered list of Issues.
    """
    __slots__ = ('data', 'issues', 'size')

    type = "issuetree"

    def __init__(self, repo, sha, issues=None):
        if len(sha) > 20:
            sha = hex_to_bin(sha)
        super(IssueTree, self).__init__(repo, sha)
        if not object_exists(self) and issues is not None:
            self.data = [{'number': i.data['number'],
                          'hexsha': i.hexsha} for i in issues]
            self.issues = issues
            serialize(self)
        else:
            deserialize(self)
            self.issues = []
            for issue in self.data:
                self.issues.append(Issue(repo, issue['hexsha']))

    @classmethod
    def create_issues_from_data(cls, repo, data):
        issues = []
        for item in data:
            for issue in item['issues']:
                result = {'filepath': item['filepath'],
                          'contents': issue}
                issues.append(Issue.create(repo, result))
        return issues

    @classmethod
    def create(cls, repo, data):
        issues = IssueTree.create_issues_from_data(repo, data)
        issues.sort()
        sha = hashlib.sha1(str(issues).encode())
        binsha = sha.digest()
        new_tree = cls(repo, binsha, issues)
        return new_tree
