# -*- coding: utf-8 -*-
"""Module that contains the definition of the issue object.

:@author: Nystrom Edwards
:Created: 23 June 2018
"""
import hashlib
import os
import re

from git import Object
from git.util import hex_to_bin

from gitissue.functions import serialize, deserialize, object_exists
from gitissue.regex import *

__all__ = ('Issue',)


def find_issue_data_in_comment(comment):
    data = {}
    number = re.findall(ISSUE_NUMBER, comment)
    if len(number) > 0:
        data['number'] = number[0]
        title = re.findall(ISSUE_TITLE, comment)
        if len(title) > 0:
            data['title'] = title[0]
        description = re.findall(ISSUE_DESCRIPTION, comment)
        if len(description) > 0:
            data['description'] = description[0]
        assignees = re.findall(ISSUE_ASSIGNEES, comment)
        if len(assignees) > 0:
            data['assignees'] = assignees[0]
        due_date = re.findall(ISSUE_DUE_DATE, comment)
        if len(due_date) > 0:
            data['due_date'] = due_date[0]
        label = re.findall(ISSUE_LABEL, comment)
        if len(label) > 0:
            data['label'] = label[0]
        weight = re.findall(ISSUE_WEIGHT, comment)
        if len(weight) > 0:
            data['weight'] = weight[0]
        priority = re.findall(ISSUE_PRIORITY, comment)
        if len(priority) > 0:
            data['priority'] = priority[0]

    return data


def get_new_issue_no(repo):
    """ Gets a new issue number for the current repository

        Args:
            :(Repo) repo: is the Repo we are located in
    """
    number_file = repo.issue_dir + '/NUMBER'

    if not os.path.exists(number_file):
        f = open(number_file, 'w')
        f.write('0')
        f.close()

    f = open(number_file, 'r')
    last_number = int(f.read())
    f.close()

    new_number = last_number + 1
    f = open(number_file, 'w')
    f.write(str(new_number))
    f.close()

    return new_number


class Issue(Object):

    __slots__ = ('data', 'number', 'title', 'description', 'assignees',
                 'due_date', 'label', 'weight', 'priority', 'title', 'size', 'filepath', 'contents', )

    type = 'issue'

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
            # self.number = get_new_issue_no(repo)
            self.data = data
            if 'number' in data:
                self.number = data['number']
            if 'title' in data:
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
            if 'number' in self.data:
                self.number = self.data['number']
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
        return self.number < other.number

    def __eq__(self, other):
        return self.binsha == other.binsha

    def __gt__(self, other):
        return self.number > other.number

    def __str__(self):
        return 'Issue#' + str(self.number) + ' ' + str(self.hexsha)

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
