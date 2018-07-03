import sys
import os
import shutil
import unittest
from unittest import TestCase
from unittest.mock import patch, Mock, MagicMock

from git import Tree, Repo
from git.util import hex_to_bin

from gitissue.commit import find_issues_in_commit_tree
from gitissue import IssueRepo, IssueTree, IssueCommit


class TestCreateIssueCommit(TestCase):

    repo = None
    issue_tree = None
    gitcommit = None

    @classmethod
    def setUpClass(cls):
        os.makedirs('here')
        os.makedirs('here/objects')

        data = [{'filepath': '.gitignore', 'issues':
                 ['the contents of the file', 'another issue', 'yet another issue']},
                {'filepath': 'file.yaml', 'issues':
                 ['the contents of the file', 'another issue', 'yet another issue']}
                ]
        cls.repo = IssueRepo()
        cls.repo.issue_dir = 'here'
        cls.repo.issue_objects_dir = 'here/objects'
        cls.issue_tree = IssueTree.create(cls.repo, data)
        cls.gitcommit = cls.repo.head.commit

    def test1_create_issue_commit(self):
        icommit = IssueCommit.create(
            self.repo, self.gitcommit, self.issue_tree)
        self.assertEqual(self.gitcommit.hexsha, icommit.hexsha)
        self.assertEqual(len(icommit.issuetree.issues), 6)
        self.assertEqual(self.gitcommit.hexsha, icommit.commit.hexsha)

    def test2_get_issue_commit_hexsha(self):
        icommit = IssueCommit(self.repo, self.gitcommit.hexsha)
        self.assertEqual(self.gitcommit.hexsha, icommit.hexsha)
        self.assertEqual(len(icommit.issuetree.issues), 6)
        self.assertEqual(self.gitcommit.hexsha, icommit.commit.hexsha)

    def test3_get_issue_commit_binsha(self):
        icommit = IssueCommit(self.repo, self.gitcommit.binsha)
        self.assertEqual(self.gitcommit.hexsha, icommit.hexsha)
        self.assertEqual(len(icommit.issuetree.issues), 6)
        self.assertEqual(self.gitcommit.hexsha, icommit.commit.hexsha)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree('here')


class TestFindIssuesInCommitTree(TestCase):

    patterns = [r'(#.*$)', ]

    def test_skips_submodule(self):
        tree = Mock()
        tree.type = 'submodule'
        matches = find_issues_in_commit_tree(tree, self.patterns)
        self.assertFalse(matches)

    def test_tree_contains_no_issues_one_file(self):
        # The magicmock helps to create an iterable object
        tree = MagicMock()
        tree.type = 'tree'

        # Builds blobs in iterable objects as a list
        mock_list = []
        for i in range(6):
            contents = 'value' + str(i)
            contents = contents.encode()
            blob = Mock()
            blob.type = 'blob'
            blob.path = '.gitignore'
            blob.data_stream = Mock()
            blob.data_stream.read = Mock(return_value=contents)
            mock_list.append(blob)

        # iterable objects set here
        tree.__iter__.return_value = mock_list

        # run the function with the mocked object
        matches = find_issues_in_commit_tree(tree, self.patterns)

        for match in matches:
            self.assertEqual(match['filepath'], '.gitignore')
            self.assertEqual(match['issues'], [])
