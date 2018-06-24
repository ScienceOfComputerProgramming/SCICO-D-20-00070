# tree.py
# Copyright (C) 2008, 2009 Michael Trier (mtrier@gmail.com) and contributors
#
# This module is part of GitPython and is released under
# the BSD License: http://www.opensource.org/licenses/bsd-license.php
import hashlib

from git import util
from git import Object
from git.util import join_path

from gitissue import Issue
from gitissue.functions import *

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
            if isinstance(item, dict):
                issues.append(Issue.create(repo, item))
                pass
            else:
                issues.append(IssueTree.create_issues_from_data(repo, item))
        return issues

    @classmethod
    def create(cls, repo, data):
        issues = IssueTree.create_issues_from_data(repo, data)
        sha = hashlib.sha1(str(issues).encode())
        binsha = sha.digest()
        new_tree = cls(issues, repo, binsha)
        try:
            serialize(new_tree)
        except RepoObjectExists:
            pass
        return new_tree
