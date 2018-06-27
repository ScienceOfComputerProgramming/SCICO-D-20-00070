import hashlib
import re

from git import util
from git import Object
from git import Commit
from git.util import hex_to_bin

from gitissue import IssueTree
from gitissue.functions import serialize, deserialize, object_exists
from gitissue.errors import RepoObjectExistsError
from gitissue.regex import MULTILINE_HASH_PYTHON_COMMENT

__all__ = ("IssueCommit")


def find_issues_in_commit_tree(commit_tree):
    matches = []
    if commit_tree.type != 'submodule':
        for item in commit_tree:
            if item.type == 'blob':

                try:
                    # read the data contained in that file
                    object_contents = item.data_stream.read().decode('utf-8')

                    # search for matches
                    matched_issues = re.findall(
                        MULTILINE_HASH_PYTHON_COMMENT,
                        object_contents)

                    # if a string match for issue found
                    if matched_issues is not None:

                        # create a dictionary with the results
                        # and add full dict to list
                        result = {'filepath': str(item.path),
                                  'issues': matched_issues}
                        matches.append(result)
                except UnicodeDecodeError:
                    pass
            else:
                # extend the list with the values to create
                # one flat list of matches
                matches.extend(find_issues_in_commit_tree(item))
    return matches


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
            self.issuetree = IssueTree(repo, self.data['issuetree_hexsha'])

    @classmethod
    def create(cls, repo, commit, issuetree):
        new_commit = cls(repo, commit.binsha, issuetree)
        return new_commit
