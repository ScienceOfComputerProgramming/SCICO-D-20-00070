# -*- coding: utf-8 -*-

import hashlib

from git import Object
from git.util import hex_to_bin, bin_to_hex

from sciit.functions import serialize_repository_object_as_json, deserialize_repository_object_from_json, \
    repository_object_exists, get_repository_object_size

__all__ = ('IssueSnapshot',)


class IssueSnapshot(Object):
    __slots__ = ('data', 'title', 'description', 'assignees', 'due_date', 'label', 'weight', 'priority', 'title', 'size'
                 , 'filepath', 'issue_id')

    def __init__(self, repo, sha, data, size):
        super(IssueSnapshot, self).__init__(repo, sha)
        self.data = data
        self.size = size

        if 'issue_id' in self.data:
            self.issue_id = self.data['issue_id']
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
        return self.issue_id < other.issue_id

    def __eq__(self, other):
        return self.issue_id == other.issue_id

    def __gt__(self, other):
        return self.issue_id > other.issue_id

    def __hash__(self):
        sha = hashlib.sha1(self.issue_id.encode())
        sha = sha.hexdigest()
        return int(sha, 16)

    def __str__(self):
        return 'Issue#' + str(self.issue_id) + ' ' + str(self.hexsha)

    @classmethod
    def create_from_hexsha(cls, repo, hexsha):
        data, size = deserialize_repository_object_from_json(repo, hexsha)

        return cls(repo, hex_to_bin(hexsha), data, size)

    @classmethod
    def create_from_binsha(cls, repo, binsha):
        data, size = deserialize_repository_object_from_json(repo, bin_to_hex(binsha).decode("utf"))
        return cls(repo, binsha, data, size)

    @classmethod
    def create_from_data(cls, repo, data):
        sha = hashlib.sha1(str(data).encode())
        hexsha = sha.hexdigest()
        data['hexsha'] = sha.hexdigest()
        if not repository_object_exists(repo, sha.hexdigest()):
            serialize_repository_object_as_json(repo, sha.hexdigest(), IssueSnapshot, data)
        return IssueSnapshot(repo, sha.digest(), data, get_repository_object_size(repo, hexsha))
