import os
import random
import string
from unittest import TestCase
from unittest.mock import Mock, MagicMock, patch

from git import Commit
from git.util import hex_to_bin
from sciit import Issue, IssueCommit, IssueRepo, IssueTree
from sciit.commit import find_issues_in_commit
from sciit.functions import write_last_issue
from tests.external_resources import safe_create_repo_dir

pattern = r'((?:#.*(?:\n\s*#)*.*)|(?:#.*)|(?:#.*$))'


class TestCreateIssueCommit(TestCase):

    @classmethod
    def setUpClass(cls):
        safe_create_repo_dir('here')
        cls.repo = IssueRepo('here')

        data = [{'id': '1', 'title': 'the contents of the file', 'filepath': 'path',
                 'description': 'This issue had a description'},
                {'id': '2', 'title': 'the contents of the file', 'filepath': 'path'},
                {'id': '3', 'title': 'the contents of the file', 'filepath': 'path'},
                {'id': '4', 'title': 'the contents of the file', 'filepath': 'path'},
                {'id': '5', 'title': 'the contents of the file', 'filepath': 'path'},
                {'id': '6',
                 'title': 'The title of your issue',
                 'description': 'A description of you issue as you\n'
                 + 'want it to be ``markdown`` supported',
                 'assignees': 'nystrome, kevin, daniels',
                 'due_date': '12 oct 2018',
                 'label': 'in-development',
                 'weight': '4',
                 'priority': 'high',
                 'filepath': 'README.md'}]

        new_data = [{'id': '1', 'title': 'the contents of the file', 'filepath': 'path'},
                    {'id': '2', 'title': 'the contents of the file', 'filepath': 'path'},
                    {'id': '9', 'title': 'the contents of the file', 'filepath': 'path'},
                    {'id': '6', 'title': 'the contents of the file', 'filepath': 'path',
                     'description': 'description has changed'},
                    {'id': '12', 'title': 'the contents of the file', 'filepath': 'path',
                     'description': 'here is a nice description'}]

        cls.issues = []
        cls.new_issues = []
        for d in data:
            cls.issues.append(Issue.create(cls.repo, d))
        cls.itree = IssueTree.create(cls.repo, cls.issues)

        for d in new_data:
            cls.new_issues.append(Issue.create(cls.repo, d))
        cls.new_itree = IssueTree.create(cls.repo, cls.new_issues)

        cls.second = '622918a4c6539f853320e06804f73d1165df69d0'
        cls.first = '43e8d11ec2cb9802151533ae8d9c5dcc5dec91a4'
        cls.second_commit = Commit(cls.repo, hex_to_bin(cls.second))
        cls.first_commit = Commit(cls.repo, hex_to_bin(cls.first))
        cls.second_icommit = IssueCommit.create(
            cls.repo, cls.second_commit, cls.new_itree)
        cls.first_icommit = IssueCommit.create(
            cls.repo, cls.first_commit, cls.itree)
        write_last_issue(cls.repo.issue_dir, cls.second)

    def test_create_issue_commit(self):
        icommit = IssueCommit.create(
            self.repo, self.first_commit, self.itree)
        self.assertEqual(self.first_commit.hexsha, icommit.hexsha)
        self.assertEqual(self.first_commit.binsha, icommit.binsha)
        self.assertEqual(len(icommit.issuetree.issues), 6)
        self.assertEqual(icommit.open_issues, 6)


class FindIssuesInCommit(TestCase):

    @classmethod
    def setUpClass(cls):
        safe_create_repo_dir('here')
        cls.repo = IssueRepo()
        cls.repo.issue_dir = 'here'
        cls.repo.issue_objects_dir = 'here/objects'

    def test_no_issues_one_changed_file(self):

        commit = Mock()
        tree = Mock()

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
        tree.blobs = mock_list
        tree.trees = []
        commit.tree = tree
        commit.stats.files.keys.return_value = [blob.path]
        commit.parents = []

        # run the function with the mocked object
        issues = find_issues_in_commit(self.repo, commit, pattern)
        self.assertFalse(issues)

    def test_one_cstyle_issue_cleaned(self):

        commit = Mock()
        tree = Mock()

        # Builds blobs in iterable objects as a list
        mock_list = []
        contents = b'/*@issue 2\n* @description \n * value that has some contents\n*/'
        blob = Mock()
        blob.path = 'hello.java'
        blob.type = 'blob'
        blob.mime_type = 'text/x-java'
        blob.data_stream = Mock()
        blob.data_stream.read = Mock(return_value=contents)
        mock_list.append(blob)

        # iterable objects set here
        tree.blobs = mock_list
        tree.trees = []
        commit.tree = tree
        commit.stats.files.keys.return_value = [blob.path]
        commit.parents = []

        # run the function with the mocked object
        issues = find_issues_in_commit(self.repo, commit)
        self.assertEqual(len(issues), 1)
        self.assertNotIn('*', issues[0].description)

    def test_one_hashstyle_issue_cleaned(self):

        commit = Mock()
        tree = Mock()

        # Builds blobs in iterable objects as a list
        mock_list = []
        contents = b'#***\n#@issue 2\n# @description \n # value that has some contents\n#***'
        blob = Mock()
        blob.path = 'hello'
        blob.type = 'blob'
        blob.mime_type = 'text/plain'
        blob.data_stream = Mock()
        blob.data_stream.read = Mock(return_value=contents)
        mock_list.append(blob)

        # iterable objects set here
        tree.blobs = mock_list
        tree.trees = []
        commit.tree = tree
        commit.stats.files.keys.return_value = [blob.path]
        commit.parents = []

        # run the function with the mocked object
        issues = find_issues_in_commit(self.repo, commit)
        self.assertEqual(len(issues), 1)
        self.assertNotIn('#', issues[0].description)

    def test_no_issues_one_changed_supported_file_no_pattern(self):

        commit = Mock()
        tree = Mock()

        # Builds blobs in iterable objects as a list
        mock_list = []
        contents = b'<!--@issue 3\nvalue that has some contents-->'
        blob = Mock()
        blob.path = 'README.md'
        blob.type = 'blob'
        blob.mime_type = 'text'
        blob.data_stream = Mock()
        blob.data_stream.read = Mock(return_value=contents)
        mock_list.append(blob)

        # iterable objects set here
        tree.blobs = mock_list
        tree.trees = []
        commit.tree = tree
        commit.stats.files.keys.return_value = [blob.path]
        commit.parents = []

        # run the function with the mocked object
        issues = find_issues_in_commit(self.repo, commit)
        self.assertEqual(len(issues), 1)

    def test_no_issues_one_changed_unsupported_file_no_pattern(self):
        commit = Mock()
        tree = Mock()

        # Builds blobs in iterable objects as a list
        mock_list = []
        contents = b'<!--@issue 3\nvalue that has some contents-->'
        blob = Mock()
        blob.path = 'picture.png'
        blob.type = 'blob'
        blob.mime_type = 'text'
        blob.data_stream = Mock()
        blob.data_stream.read = Mock(return_value=contents)
        mock_list.append(blob)

        # iterable objects set here
        tree.blobs = mock_list
        tree.trees = []
        commit.tree = tree
        commit.stats.files.keys.return_value = [blob.path]
        commit.parents = []

        # run the function with the mocked object
        issues = find_issues_in_commit(self.repo, commit)
        self.assertFalse(issues)

    def test_no_issues_multiple_changed_files(self):

        commit = Mock()
        tree = Mock()

        # Builds blobs in iterable objects as a list
        mock_list = []
        for i in range(6):
            contents = ''.join(random.SystemRandom().choice(
                string.ascii_letters + string.digits) for _ in range(40))
            contents = contents.encode()
            blob = Mock()
            blob.path = 'README'+str(i)
            blob.type = 'blob'
            blob.mime_type = 'text'
            blob.data_stream = Mock()
            blob.data_stream.read = Mock(return_value=contents)
            mock_list.append(blob)

        # iterable objects set here
        tree.blobs = mock_list
        tree.trees = []
        commit.tree = tree
        commit.stats.files.keys.return_value = ['README1', 'README3']
        commit.parents = []

        # run the function with the mocked object
        issues = find_issues_in_commit(self.repo, commit, pattern)
        self.assertFalse(issues)

    def test_no_issues_renamed_file_change(self):

        commit = Mock()
        tree = Mock()

        # Builds blobs in iterable objects as a list
        mock_list = []
        for i in range(6):
            contents = ''.join(random.SystemRandom().choice(
                string.ascii_letters + string.digits) for _ in range(40))
            contents = contents.encode()
            blob = Mock()
            blob.path = 'README'+str(i)
            blob.type = 'blob'
            blob.mime_type = 'text'
            blob.data_stream = Mock()
            blob.data_stream.read = Mock(return_value=contents)
            mock_list.append(blob)

        # iterable objects set here
        tree.blobs = mock_list
        tree.trees = []
        commit.tree = tree
        commit.stats.files.keys.return_value = ['docs/this.py', 'README3']
        commit.parents = []

        # run the function with the mocked object
        issues = find_issues_in_commit(self.repo, commit, pattern)
        self.assertFalse(issues)

    def test_no_issues_multiple_changed_files_in_trees(self):

        commit = Mock()
        tree = Mock()

        # Builds blobs in iterable objects as a list
        mock_list = []
        for i in range(6):
            contents = ''.join(random.SystemRandom().choice(
                string.ascii_letters + string.digits) for _ in range(40))
            contents = contents.encode()
            blob = Mock()
            blob.path = 'README'+str(i)
            blob.type = 'blob'
            blob.mime_type = 'text'
            blob.data_stream = Mock()
            blob.data_stream.read = Mock(return_value=contents)
            mock_list.append(blob)

        # iterable objects set here
        tree.blobs = mock_list.copy()
        mock_list = []
        for i in range(12):
            contents = ''.join(random.SystemRandom().choice(
                string.ascii_letters + string.digits) for _ in range(40))
            contents = contents.encode()
            blob = Mock()
            blob.path = 'docs/file'+str(i)+'.py'
            blob.type = 'blob'
            blob.mime_type = 'text'
            blob.data_stream = Mock()
            blob.data_stream.read = Mock(return_value=contents)
            mock_list.append(blob)
        new_tree = Mock()
        new_tree.trees = []
        new_tree.blobs = mock_list
        tree.trees = [new_tree]
        commit.tree = tree
        commit.stats.files.keys.return_value = [
            'README1', 'README3', 'docs/file9.py']
        commit.parents = []

        # run the function with the mocked object
        issues = find_issues_in_commit(self.repo, commit, pattern)
        self.assertFalse(issues)

    def test_skips_unicode_error_one_file(self):

        commit = Mock()
        tree = Mock()

        # Builds blobs in iterable objects as a list
        mock_list = []
        contents = 'value that has some contents'
        blob = Mock()
        blob.path = 'README'
        blob.type = 'blob'
        blob.mime_type = 'text'
        blob.data_stream = Mock()
        blob.data_stream.read = Mock(return_value=contents)
        mock_list.append(blob)

        # iterable objects set here
        tree.blobs = mock_list
        tree.trees = []
        commit.tree = tree
        commit.stats.files.keys.return_value = [blob.path]
        commit.parents = []

        # run the function with the mocked object
        issues = find_issues_in_commit(self.repo, commit, pattern)
        self.assertFalse(issues)

    def test_contains_issues_multiple_changed_files(self):
        commit = Mock()
        tree = Mock()

        # Builds blobs in iterable objects as a list
        mock_list = []
        for i in range(6):
            contents = '#@issue ' + str(i)
            contents = contents.encode()
            blob = Mock()
            blob.path = 'README'+str(i)
            blob.type = 'blob'
            blob.mime_type = 'text'
            blob.data_stream = Mock()
            blob.data_stream.read = Mock(return_value=contents)
            mock_list.append(blob)
        mock_list[3].contents = b'This one has no issue in it'

        # iterable objects set here
        tree.blobs = mock_list
        tree.trees = []
        commit.tree = tree
        commit.stats.files.keys.return_value = [
            'README0', 'README1', 'README2']
        commit.parents = []

        # run the function with the mocked object
        issues = find_issues_in_commit(self.repo, commit, pattern)
        self.assertEqual(len(issues), 3)

    def test_contains_issues_multiple_changed_files_multiple_trees(self):
        commit = Mock()
        tree = Mock()

        # Builds blobs in iterable objects as a list
        mock_list = []
        for i in range(6):
            contents = '#@issue ' + str(i)
            contents = contents.encode()
            blob = Mock()
            blob.path = 'README'+str(i)
            blob.type = 'blob'
            blob.mime_type = 'text'
            blob.data_stream = Mock()
            blob.data_stream.read = Mock(return_value=contents)
            mock_list.append(blob)
        mock_list[3].contents = b'This one has no issue in it'

        # iterable objects set here
        tree.blobs = mock_list.copy()
        mock_list = []
        for i in range(12):
            contents = '#@issue w'+str(i)
            contents = contents.encode()
            blob = Mock()
            blob.path = 'docs/file'+str(i)+'.py'
            blob.type = 'blob'
            blob.mime_type = 'text'
            blob.data_stream = Mock()
            blob.data_stream.read = Mock(return_value=contents)
            mock_list.append(blob)
        new_tree = Mock()
        new_tree.trees = []
        new_tree.blobs = mock_list
        tree.trees = [new_tree]
        commit.tree = tree
        commit.stats.files.keys.return_value = [
            'README0', 'README1', 'README2', 'docs/file3.py', 'docs/file7.py']
        commit.parents = []

        # run the function with the mocked object
        issues = find_issues_in_commit(self.repo, commit, pattern)
        self.assertEqual(len(issues), 5)

    def test_tree_contains_no_issues_multiple_files_nested_folder(self):
        pass

    def test_tree_contains_multiple_issues_one_file(self):
        pass

    def test_tree_contains_one_non_text_file(self):
        pass

    def test_tree_contains_multiple_issues_multiple_files(self):
        pass

    def test_tree_contains_multiple_issues_multiple_files_nested_folder(self):
        pass
