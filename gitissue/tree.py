import hashlib

from git import util
from git import Object
from git.util import join_path

from gitissue import Issue
from gitissue.functions import serialize
from gitissue.errors import RepoObjectExistsError

__all__ = ("IssueTree")


class IssueTree(Object):
    """IssueTree objects represent an ordered list of Issues.
    """

    type = "issuetree"

    def __init__(self, issues, repo, binsha):
        super(IssueTree, self).__init__(repo, binsha)
        if issues is not None:
            self.data = str(issues)
            self.issues = issues

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
        new_tree = cls(issues, repo, binsha)
        try:
            serialize(new_tree)
        except RepoObjectExistsError:
            pass
        return new_tree
