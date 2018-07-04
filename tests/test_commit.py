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

    patterns = [r'((?:#.*(?:\n\s*#)*.*)|(?:#.*)|(?:#.*$))', ]

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
        contents = b'value that has some contents'
        blob = Mock()
        blob.path = 'README'
        blob.type = 'blob'
        blob.data_stream = Mock()
        blob.data_stream.read = Mock(return_value=contents)
        mock_list.append(blob)

        # iterable objects set here
        tree.__iter__.return_value = mock_list

        # run the function with the mocked object
        matches = find_issues_in_commit_tree(tree, self.patterns)

        for match in matches:
            self.assertEqual(match['issues'], [])

    def test_tree_contains_unicode_error_one_file(self):
        # The magicmock helps to create an iterable object
        tree = MagicMock()
        tree.type = 'tree'

        # Builds blobs in iterable objects as a list
        mock_list = []
        contents = '23412342'  # here is the error data
        blob = Mock()
        blob.path = 'README'
        blob.type = 'blob'
        blob.data_stream = Mock()
        blob.data_stream.read = Mock(return_value=contents)
        mock_list.append(blob)

        # iterable objects set here
        tree.__iter__.return_value = mock_list

        # run the function with the mocked object
        matches = find_issues_in_commit_tree(tree, self.patterns)
        self.assertEqual(matches, [])

    def test_tree_contains_no_issues_multiple_files(self):
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
            blob.data_stream = Mock()
            blob.data_stream.read = Mock(return_value=contents)
            mock_list.append(blob)
        mock_list[0].path = '.gitignore'
        mock_list[1].path = 'README'
        mock_list[2].path = '.travis.yaml'
        mock_list[3].path = 'test.py'
        mock_list[4].path = 'hello.py'
        mock_list[5].path = 'functions.py'

        # iterable objects set here
        tree.__iter__.return_value = mock_list

        # run the function with the mocked object
        matches = find_issues_in_commit_tree(tree, self.patterns)

        for match in matches:
            self.assertEqual(match['issues'], [])

    def test_tree_contains_no_issues_multiple_files_nested_folder(self):
        # The magicmock helps to create an iterable object
        tree = MagicMock()
        tree.type = 'tree'

        # Builds blobs in iterable objects as a list
        mock_list = []
        contents = b'The project consists of contents'
        blob = Mock()
        blob.type = 'blob'
        blob.path = 'README'
        blob.data_stream = Mock()
        blob.data_stream.read = Mock(return_value=contents)
        mock_list.append(blob)

        # Builds a tree within the tree as folder structure
        t = MagicMock()
        t.type = 'tree'

        # fill folder files with contents
        tree_list = []
        for i in range(2):
            contents = 'some contents for the file' + str(i)
            contents = contents.encode()
            blob = Mock()
            blob.type = 'blob'
            blob.data_stream = Mock()
            blob.data_stream.read = Mock(return_value=contents)
            tree_list.append(blob)
        tree_list[0].path = 'src/file.py'
        tree_list[1].path = 'src/main.py'

        # Make folder iterable
        t.__iter__.return_value = tree_list

        # Add tree to upper level tree
        mock_list.append(t)

        # iterable objects set here
        tree.__iter__.return_value = mock_list

        # run the function with the mocked object
        matches = find_issues_in_commit_tree(tree, self.patterns)

        for match in matches:
            self.assertEqual(match['issues'], [])

    def test_tree_contains_multiple_issues_one_file(self):
        # The magicmock helps to create an iterable object
        tree = MagicMock()
        tree.type = 'tree'

        # Builds blobs in iterable objects as a list
        mock_list = []
        contents = b'#value that has some contents\ndoggy #the issue here as well'
        blob = Mock()
        blob.path = 'README'
        blob.type = 'blob'
        blob.data_stream = Mock()
        blob.data_stream.read = Mock(return_value=contents)
        mock_list.append(blob)

        # iterable objects set here
        tree.__iter__.return_value = mock_list

        # run the function with the mocked object
        matches = find_issues_in_commit_tree(tree, self.patterns)
        self.assertEqual(len(matches[0]['issues']), 2)

    def test_tree_contains_multiple_issues_multiple_file(self):
        # The magicmock helps to create an iterable object
        tree = MagicMock()
        tree.type = 'tree'

        # Builds blobs in iterable objects as a list
        mock_list = []
        for i in range(3):
            contents = b'#value that has some contents\ndoggy #the issue here as well'
            blob = Mock()
            blob.type = 'blob'
            blob.data_stream = Mock()
            blob.data_stream.read = Mock(return_value=contents)
            mock_list.append(blob)
        mock_list[0].path = 'README'
        mock_list[1].path = '.gitignore'
        mock_list[2].path = 'hello.java'

        # iterable objects set here
        tree.__iter__.return_value = mock_list

        # run the function with the mocked object
        matches = find_issues_in_commit_tree(tree, self.patterns)
        self.assertEqual(len(matches[0]['issues']), 2)
        self.assertEqual(len(matches[1]['issues']), 2)
        self.assertEqual(len(matches[2]['issues']), 2)

    def test_tree_contains_multiple_issues_multiple_files_nested_folder(self):
        # The magicmock helps to create an iterable object
        tree = MagicMock()
        tree.type = 'tree'

        # Builds blobs in iterable objects as a list
        mock_list = []
        contents = b'#The project \nhello #consists of contents\n contents #here'
        blob = Mock()
        blob.type = 'blob'
        blob.path = 'README'
        blob.data_stream = Mock()
        blob.data_stream.read = Mock(return_value=contents)
        mock_list.append(blob)

        # Builds a tree within the tree as folder structure
        t = MagicMock()
        t.type = 'tree'

        # fill folder files with contents
        tree_list = []
        for i in range(2):
            contents = '#some contents for the file' + str(i)
            contents = contents.encode()
            blob = Mock()
            blob.type = 'blob'
            blob.data_stream = Mock()
            blob.data_stream.read = Mock(return_value=contents)
            tree_list.append(blob)
        tree_list[0].path = 'src/file.py'
        tree_list[1].path = 'src/main.py'

        # Make folder iterable
        t.__iter__.return_value = tree_list

        # Add tree to upper level tree
        mock_list.append(t)

        # iterable objects set here
        tree.__iter__.return_value = mock_list

        # run the function with the mocked object
        matches = find_issues_in_commit_tree(tree, self.patterns)
        self.assertEqual(len(matches[0]['issues']), 3)
        self.assertEqual(len(matches[1]['issues']), 1)
        self.assertEqual(len(matches[2]['issues']), 1)
