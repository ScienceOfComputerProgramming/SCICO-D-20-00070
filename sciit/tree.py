# -*- coding: utf-8 -*-
"""Module that contains the definition of the issue tree.

:@author: Nystrom Edwards
:Created: 24 June 2018
"""
import hashlib

from git import util, Object
from git.util import hex_to_bin, bin_to_hex

from sciit import Issue
from sciit.functions import serialize_repository_object_as_json, deserialize_repository_object_from_json, \
    repository_object_exists, get_repository_object_size


__all__ = ('IssueTree', )


class IssueTree(Object):

    __slots__ = ('data', 'issues', 'size')

    def __init__(self, repo, sha, issues, size):
        super(IssueTree, self).__init__(repo, sha)
        self.issues = issues
        self.size = size

    @classmethod
    def create_from_issues(cls, repo, issues):

        issues = list(set(issues))
        issues.sort()
        sha = hashlib.sha1(str(issues).encode())
        binsha = sha.digest()
        hexsha = sha.hexdigest()
        if not repository_object_exists(repo, hexsha):
            data = [{'id': i.data['id'], 'hexsha': i.hexsha} for i in issues]
            serialize_repository_object_as_json(repo, hexsha, IssueTree, data)

        size = get_repository_object_size(repo, hexsha)
        return cls(repo, binsha, issues, size)

    @classmethod
    def create_from_data(cls, repo, data):
        issues = list()
        for issue_data in data:
            issues.append(Issue.create_from_hexsha(repo, issue_data['hexsha']))

        return IssueTree.create_from_issues(repo, issues)

    @classmethod
    def create_from_binsha(cls, repo, binsha):
        hexsha = bin_to_hex(binsha).decode("utf")
        return IssueTree.create_from_shas(repo, hexsha, binsha)

    @classmethod
    def create_from_hexsha(cls, repo, hexsha):
        binsha = hex_to_bin(hexsha)
        return IssueTree.create_from_shas(repo, hexsha, binsha)

    @classmethod
    def create_from_shas(cls, repo, hexsha, binsha):
        data, size = deserialize_repository_object_from_json(repo, hexsha)

        issues = list()
        for issue_data in data:
            issues.append(Issue.create_from_hexsha(repo, issue_data['hexsha']))

        return cls(repo, binsha, issues, size)

