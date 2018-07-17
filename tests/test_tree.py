import sys
import os
import shutil
from unittest import TestCase
from unittest.mock import patch, Mock, MagicMock
from gitissue import IssueRepo, IssueTree, Issue
from gitissue.tree import find_issues_in_tree


class TestCreateIssueTree(TestCase):

    repo = None
    issue_sha = None
    issues = None

    @classmethod
    def setUpClass(cls):
        os.makedirs('here')
        os.makedirs('here/objects')

        data = [{'id': '1', 'title': 'the contents of the file'},
                {'id': '2', 'title': 'the contents of the file'},
                {'id': '3', 'title': 'the contents of the file'},
                {'id': '4', 'title': 'the contents of the file'},
                {'id': '5', 'title': 'the contents of the file'},
                {'id': '6', 'title': 'the contents of the file'}]
        cls.repo = IssueRepo()
        cls.repo.issue_dir = 'here'
        cls.repo.issue_objects_dir = 'here/objects'
        cls.issues = []
        for issue_data in data:
            cls.issues.append(Issue.create(cls.repo, issue_data))

    def test1_create_issue_tree(self):
        itree = IssueTree.create(self.repo, self.issues)
        self.assertEqual(len(itree.issues), 6)
        TestCreateIssueTree.issue_sha = (itree.binsha, itree.hexsha)

    def test2_get_issue_tree_binsha(self):
        itree = IssueTree(self.repo, TestCreateIssueTree.issue_sha[0])
        self.assertEqual(len(itree.issues), 6)

    def test2_get_issue_tree_hexsha(self):
        itree = IssueTree(self.repo, TestCreateIssueTree.issue_sha[1])
        self.assertEqual(len(itree.issues), 6)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree('here')


class TestFindIssuesInTree(TestCase):

    pattern = r'((?:#.*(?:\n\s*#)*.*)|(?:#.*)|(?:#.*$))'
    repo = None

    @classmethod
    def setUpClass(cls):
        os.makedirs('here')
        os.makedirs('here/objects')
        cls.repo = IssueRepo()
        cls.repo.issue_dir = 'here'
        cls.repo.issue_objects_dir = 'here/objects'

    def test_skips_submodule(self):
        tree = Mock()
        tree.type = 'submodule'
        issues = find_issues_in_tree(self.repo, tree, self.pattern)
        self.assertFalse(issues)

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
        blob.mime_type = 'text'
        blob.data_stream = Mock()
        blob.data_stream.read = Mock(return_value=contents)
        mock_list.append(blob)

        # iterable objects set here
        tree.__iter__.return_value = mock_list

        # run the function with the mocked object
        issues = find_issues_in_tree(self.repo, tree, self.pattern)
        self.assertFalse(issues)

    def test_tree_skips_unicode_error_one_file(self):
        # The magicmock helps to create an iterable object
        tree = MagicMock()
        tree.type = 'tree'

        # Builds blobs in iterable objects as a list
        mock_list = []
        contents = '23412342'  # here is the error data
        blob = Mock()
        blob.path = 'README'
        blob.type = 'blob'
        blob.mime_type = 'text'
        blob.data_stream = Mock()
        blob.data_stream.read = Mock(return_value=contents)
        mock_list.append(blob)

        # iterable objects set here
        tree.__iter__.return_value = mock_list

        # run the function with the mocked object
        issues = find_issues_in_tree(self.repo, tree, self.pattern)
        self.assertFalse(issues)

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
            blob.mime_type = 'text'
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
        issues = find_issues_in_tree(self.repo, tree, self.pattern)
        self.assertFalse(issues)

    def test_tree_contains_no_issues_multiple_files_nested_folder(self):
        # The magicmock helps to create an iterable object
        tree = MagicMock()
        tree.type = 'tree'

        # Builds blobs in iterable objects as a list
        mock_list = []
        contents = b'The project consists of contents'
        blob = Mock()
        blob.type = 'blob'
        blob.mime_type = 'text'
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
            blob.mime_type = 'text'
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
        issues = find_issues_in_tree(self.repo, tree, self.pattern)
        self.assertFalse(issues)

    def test_tree_contains_multiple_issues_one_file(self):
        # The magicmock helps to create an iterable object
        tree = MagicMock()
        tree.type = 'tree'

        # Builds blobs in iterable objects as a list
        mock_list = []
        contents = b'# @issue_no: 1 \nvalue that has some contents\n# @issue 2\n here as well'
        blob = Mock()
        blob.path = 'README'
        blob.type = 'blob'
        blob.mime_type = 'text'
        blob.data_stream = Mock()
        blob.data_stream.read = Mock(return_value=contents)
        mock_list.append(blob)

        # iterable objects set here
        tree.__iter__.return_value = mock_list

        # run the function with the mocked object
        issues = find_issues_in_tree(self.repo, tree, self.pattern)
        self.assertEqual(len(issues), 2)

    def test_tree_contains_one_non_text_file(self):
        # The magicmock helps to create an iterable object
        tree = MagicMock()
        tree.type = 'tree'

        # Builds blobs in iterable objects as a list
        mock_list = []
        contents = b'# @issue_no: 1 \nvalue that has some contents\n# @issue 2\n here as well'
        blob = Mock()
        blob.path = 'README'
        blob.type = 'blob'
        blob.mime_type = 'application/json'
        blob.data_stream = Mock()
        blob.data_stream.read = Mock(return_value=contents)
        mock_list.append(blob)

        # iterable objects set here
        tree.__iter__.return_value = mock_list

        # run the function with the mocked object
        issues = find_issues_in_tree(self.repo, tree, self.pattern)
        self.assertEqual(len(issues), 2)

    def test_tree_contains_multiple_issues_multiple_files(self):
        # The magicmock helps to create an iterable object
        tree = MagicMock()
        tree.type = 'tree'

        # Builds blobs in iterable objects as a list
        mock_list = []
        for i in range(3):
            contents = '#@issue_no: ' + \
                str(i) + ' value that has some contents\n#the issue' \
                'here as well\n\n\n\ntext text\n\n\n# @issue ' + str((i+1)*2)
            contents = contents.encode()
            blob = Mock()
            blob.type = 'blob'
            blob.mime_type = 'text'
            blob.data_stream = Mock()
            blob.data_stream.read = Mock(return_value=contents)
            mock_list.append(blob)
        mock_list[0].path = 'README'
        mock_list[1].path = '.gitignore'
        mock_list[2].path = 'hello.java'

        # iterable objects set here
        tree.__iter__.return_value = mock_list

        # run the function with the mocked object
        issues = find_issues_in_tree(self.repo, tree, self.pattern)
        self.assertEqual(len(issues), 6)

    def test_tree_contains_multiple_issues_multiple_files_nested_folder(self):
        # The magicmock helps to create an iterable object
        tree = MagicMock()
        tree.type = 'tree'

        # Builds blobs in iterable objects as a list
        mock_list = []
        contents = b'#@issue 9 The project \ndoggy# @issue 20 consists of contents\n contents #here'
        blob = Mock()
        blob.type = 'blob'
        blob.mime_type = 'text'
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
            contents = '#some contents for the file @issue ' + str(i)
            contents = contents.encode()
            blob = Mock()
            blob.type = 'blob'
            blob.mime_type = 'text'
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
        issues = find_issues_in_tree(self.repo, tree, self.pattern)
        self.assertEqual(len(issues), 4)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree('here')
