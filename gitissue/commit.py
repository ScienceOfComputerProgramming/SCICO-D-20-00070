# -*- coding: utf-8 -*-
"""Module that contains the definition of the issue commit.

:@author: Nystrom Edwards
:Created: 24 June 2018
"""


import hashlib

from git import util, Object, Commit
from git.util import hex_to_bin

from gitissue import IssueTree
from gitissue.functions import serialize, deserialize, object_exists

__all__ = ("IssueCommit")


class IssueCommit(Object):
    """IssueCommit objects represent a git commit object linked to an
    IssueTree.
    :note:
        When creating a tree if the object already exists the
        existing object is returned
    """
    __slots__ = ('data', 'commit', 'size', 'issuetree')

    type = "issuecommit"

    def __init__(self, repo, sha, issuetree=None):
        """Initialize a newly instanced IssueCommiy

        Args:
            :(Repo) repo: is the Repo we are located in
            :(bytes/str) sha: 20 byte binary sha1 or 40 character hexidecimal sha1
            :(IssueTree) issuetree:
                the issue tree that contains all the issue contents for this commit
        :note:
            The object may be deserialised from the file system when instatiated 
            or serialized to the file system when the object is created from a factory
        """
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
        """Factory method that creates an IssueCommit with its issuetree
        or return the IssueCommit from the FileSystem

        Args:
            :(Repo) repo: is the Repo we are located in
            :(Commit) commit: is the git commit that we are linking to
            :(IssueTree) issuetree:
                the issue tree that contains all the issue contents for this commit
        """
        new_commit = cls(repo, commit.binsha, issuetree)
        return new_commit
