# -*- coding: utf-8 -*-
"""Module that contains the definition of the issue object.

:@author: Nystrom Edwards
:Created: 23 June 2018
"""
import hashlib
import os

from git import Object
from git.util import hex_to_bin

from gitissue.functions import serialize, deserialize, object_exists

__all__ = ('Issue',)


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

    __slots__ = ('data', 'filepath', 'contents', 'number', 'size')

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
            self.number = get_new_issue_no(repo)
            data['number'] = self.number
            self.data = data
            self.filepath = data['filepath']
            self.contents = data['contents']
            serialize(self)
        else:
            deserialize(self)
            self.number = self.data['number']
            self.filepath = self.data['filepath']
            self.contents = self.data['contents']

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
