# -*- coding: utf-8 -*-
"""Module that contains the definition of the issue object.

:@author: Nystrom Edwards
:Created: 23 June 2018
"""
import hashlib
import re

from git import Object
from git.util import hex_to_bin
from slugify import slugify

from sciit.functions import serialize, deserialize, object_exists
from sciit.regex import ISSUE

__all__ = ('Issue', 'find_issue_data_in_comment', )


def find_issue_data_in_comment(comment):
    """Finds the relevant issue data in block comments
    made by the user in source code. Only if an issue
    is specified does the function continue to extract
    other issue data.

    Args:
        :(str) comment: raw string representation of \
        the block comment

    Returns:
        :(dict) data: contains all the relevant issue data
    """
    data = {}
    ident = re.findall(ISSUE.ID, comment)
    if len(ident) > 0:
        data['id'] = slugify(ident[0])
        title = re.findall(ISSUE.TITLE, comment)
        if len(title) > 0:
            data['title'] = title[0]
        else:
            data['title'] = ident[0]
        description = re.findall(ISSUE.DESCRIPTION, comment)
        if len(description) > 0:
            description = re.sub(r'\n +', '\n', description[0])
            data['description'] = description
        assignees = re.findall(ISSUE.ASSIGNEES, comment)
        if len(assignees) > 0:
            data['assignees'] = assignees[0]
        due_date = re.findall(ISSUE.DUE_DATE, comment)
        if len(due_date) > 0:
            data['due_date'] = due_date[0]
        label = re.findall(ISSUE.LABEL, comment)
        if len(label) > 0:
            data['label'] = label[0]
        weight = re.findall(ISSUE.WEIGHT, comment)
        if len(weight) > 0:
            data['weight'] = weight[0]
        priority = re.findall(ISSUE.PRIORITY, comment)
        if len(priority) > 0:
            data['priority'] = priority[0]

    return data


class Issue(Object):

    __slots__ = ('data', 'title', 'description', 'assignees',
                 'due_date', 'label', 'weight', 'priority', 'title',
                 'size', 'filepath', 'id')

    type = 'issue'
    """ The base type of this issue repository object
    """

    def __init__(self, repo, sha, data=None):
        """Issue objects represent the issue created by a user and all
        of its metadata
        :note:
            When creating a issue if the object already exists the
            existing object is returned
        """
        if len(sha) > 20:
            sha = hex_to_bin(sha)
        super(Issue, self).__init__(repo, sha)
        if not object_exists(self) and data is not None:
            self.data = data
            """Dictionary containing issue data that is easily
            serializable/deserializable
            """
            data['hexsha'] = self.hexsha
            self.id = data['id']
            self.title = data['title']
            if 'description' in data:
                self.description = data['description']
            if 'assignees' in data:
                self.assignees = data['assignees']
            if 'due_date' in data:
                self.due_date = data['due_date']
            if 'label' in data:
                self.label = data['label']
            if 'weight' in data:
                self.weight = data['weight']
            if 'priority' in data:
                self.priority = data['priority']
            if 'filepath' in data:
                self.filepath = data['filepath']
            serialize(self)
        else:
            deserialize(self)
            if 'id' in self.data:
                self.id = self.data['id']
            if 'title' in self.data:
                self.title = self.data['title']
            if 'description' in self.data:
                self.description = self.data['description']
            if 'assignees' in self.data:
                self.assignees = self.data['assignees']
            if 'due_date' in self.data:
                self.due_date = self.data['due_date']
            if 'label' in self.data:
                self.label = self.data['label']
            if 'weight' in self.data:
                self.weight = self.data['weight']
            if 'priority' in self.data:
                self.priority = self.data['priority']
            if 'filepath' in self.data:
                self.filepath = self.data['filepath']

    def __lt__(self, other):
        return self.id < other.id

    def __eq__(self, other):
        return self.id == other.id

    def __gt__(self, other):
        return self.id > other.id

    def __hash__(self):
        sha = hashlib.sha1(self.id.encode())
        sha = sha.hexdigest()
        return int(sha, 16)

    def __str__(self):
        return 'Issue#' + str(self.id) + ' ' + str(self.hexsha)

    @classmethod
    def create(cls, repo, data):
        """Factory method that creates an IssueTree with its issues
        or return the IssueTree From the FileSystem

        Args:
            :(Repo) repo: is the Repo we are located in
            :(dict{}) data: a dictionary with issue contents
        """
        sha = hashlib.sha1(str(data).encode())
        binsha = sha.digest()
        new_issue = cls(repo, binsha, data)
        return new_issue
