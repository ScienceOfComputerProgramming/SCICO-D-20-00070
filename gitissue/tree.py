# -*- coding: utf-8 -*-
"""Module that contains the definition of the issue tree.

:@author: Nystrom Edwards
:Created: 24 June 2018
"""
import hashlib
import re

from git import util, Object
from git.util import hex_to_bin

from gitissue import Issue
from gitissue.issue import find_issue_data_in_comment
from gitissue.functions import serialize, deserialize, object_exists


__all__ = ("IssueTree")


def find_issues_in_tree(repo, commit_tree, patterns):
    """
    Recursively traverse the tree of files specified in a commit object's tree and
    search for patterns that identify an issue.

    Args:
        :(CommitTree) commit_tree: The tree object of a git commit
        :(list) patterns: list of regex patterns to match

    Returns:
        :(list(Issues)) issues: a list of issues
    """
    issues = []
    if commit_tree.type != 'submodule':
        for file_object in commit_tree:
            if file_object.type == 'blob':

                try:
                    # read the data contained in that file
                    object_contents = file_object.data_stream.read().decode('utf-8')
                except (UnicodeDecodeError, AttributeError):
                    continue

                # search for comment blocks in file
                comments = []
                for pattern in patterns:
                    comments.extend(
                        re.findall(pattern, object_contents))

                # if a comment block is found in the file
                if comments is not None:

                    # search for issues embedded within the comments

                    for comment in comments:
                        issue_data = find_issue_data_in_comment(comment)
                        if issue_data:
                            issue_data['filepath'] = file_object.path
                            issue = Issue.create(repo, issue_data)
                            issues.append(issue)
            else:
                # extend the list with the values to create
                # one flat list of matches
                issues.extend(find_issues_in_tree(
                    repo, file_object, patterns))
    return issues


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
    def create(cls, repo, issues):
        """Factory method that creates an IssueTree with its issues
        or return the IssueTree From the FileSystem

        Args:
            :(Repo) repo: is the Repo we are located in
            :(list(Issues)) issues: a list of issues that are associated 
            to this commit tree
        """
        issues.sort()
        sha = hashlib.sha1(str(issues).encode())
        binsha = sha.digest()
        new_tree = cls(repo, binsha, issues)
        return new_tree
