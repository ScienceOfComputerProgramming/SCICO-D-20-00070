# -*- coding: utf-8 -*-
"""Module that contains the definition of the issue tree.

:@author: Nystrom Edwards
:Created: 24 June 2018
"""
import hashlib
import re
import os

from git import util, Object
from git.util import hex_to_bin

from sciit import Issue
from sciit.issue import find_issue_data_in_comment
from sciit.functions import serialize, deserialize, object_exists
from sciit.regex import get_file_object_pattern, PLAIN


__all__ = ('IssueTree', )


class IssueTree(Object):
    """IssueTree objects represent an ordered list of Issues.

    :note:
        When creating a tree if the object already exists the
        existing object is returned
    """
    __slots__ = ('data', 'issues', 'size')

    type = 'issuetree'
    """ The base type of this issue repository object
    """

    def __init__(self, repo, sha, issues=None):
        """Initialize a newly instanced IssueTree

        Args:
            :(Repo) repo: is the Repo we are located in
            :(bytes/str) sha: 20 byte binary sha1 or 40 character hexidecimal sha1
            :(list) issues:
                a list of issues as issue objects

        :note:
            The object may be deserialised from the file system when instatiated 
            or serialized to the file system when the object is created from a factory
        """
        if len(sha) > 20:
            sha = hex_to_bin(sha)
        super(IssueTree, self).__init__(repo, sha)
        if not object_exists(self) and issues is not None:
            self.data = [{'id': i.data['id'],
                          'hexsha': i.hexsha} for i in issues]
            """List of dictionaries containing issue data that is easily
            serializable/deserializable
            """
            self.issues = issues
            """The :py:class:`Issues` that are attached to this issue tree
            """
            serialize(self)
        else:
            deserialize(self)
            self.issues = []
            for issue in self.data:
                self.issues.append(Issue(repo, issue['hexsha']))

    @classmethod
    def create(cls, repo, issues):
        """Factory method that creates an IssueTree with its issues.

        Args:
            :(Repo) repo: is the Repo we are located in
            :(list(Issues)) issues: a list of issues that are \
            associated to this commit tree
        """
        if issues:
            issues = list(set(issues))
            issues.sort()
            sha = hashlib.sha1(str(issues).encode())
            binsha = sha.digest()
            new_tree = cls(repo, binsha, issues)
            return new_tree
        else:
            new_tree = cls(repo, cls.NULL_BIN_SHA, [])
            return new_tree
