# -*- coding: utf-8 -*-
"""Module that contains the definition of the issue tree.

:@author: Nystrom Edwards
:Created: 24 June 2018
"""
import hashlib

from git import util, Object
from git.util import hex_to_bin

from gitissue import Issue
from gitissue.functions import serialize, deserialize, object_exists

__all__ = ("IssueTree")


class IssueTree(Object):
    """IssueTree objects represent an ordered list of Issues.
    :note:
        When creating a tree if the object already exists the
        existing object is returned
    """
    __slots__ = ('data', 'issues', 'size')

    type = "issuetree"

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
        """Create issues from data found in regex matches

        Args:
            :(Repo) repo: is the Repo we are located in
            :(list(dict{})) data: a list of issues in a file which contains a list of dictionaries with
                     issue contents
        """
        issues = []
        for item in data:
            for issue in item['issues']:
                result = {'filepath': item['filepath'],
                          'contents': issue}
                issues.append(Issue.create(repo, result))
        return issues

    @classmethod
    def create(cls, repo, data):
        """Factory method that creates an IssueTree with its issues
        or return the IssueTree From the FileSystem

        Args:
            :(Repo) repo: is the Repo we are located in
            :(list(dict{})) data: a list of issues in a file which contains a list of dictionaries with
                     issue contents
        """
        issues = IssueTree.create_issues_from_data(repo, data)
        issues.sort()
        sha = hashlib.sha1(str(issues).encode())
        binsha = sha.digest()
        new_tree = cls(repo, binsha, issues)
        return new_tree
