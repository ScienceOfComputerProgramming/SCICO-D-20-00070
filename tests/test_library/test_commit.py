import os
from unittest import TestCase
from unittest.mock import Mock, MagicMock, patch

from git import Repo, Tree
from sciit import Issue, IssueCommit, IssueRepo, IssueTree
from sciit.commit import find_issues_in_commit
from tests.external_resources import safe_create_repo_dir

pattern = r'((?:#.*(?:\n\s*#)*.*)|(?:#.*)|(?:#.*$))'


class TestCreateIssueCommit(TestCase):

    @classmethod
    def setUpClass(cls):
        safe_create_repo_dir('here')

        data = [{'id': '1', 'title': 'the contents of the file'},
                {'id': '2', 'title': 'the contents of the file'},
                {'id': '3', 'title': 'the contents of the file'},
                {'id': '4', 'title': 'the contents of the file'},
                {'id': '5', 'title': 'the contents of the file'},
                {'id': '6', 'title': 'the contents of the file'}]
        cls.repo = IssueRepo(issue_dir='here')
        issues = []
        for issue_data in data:
            issues.append(Issue.create(cls.repo, issue_data))
        cls.issue_tree = IssueTree.create(cls.repo, issues)
        cls.gitcommit = cls.repo.head.commit

    def test_create_issue_commit(self):
        icommit = IssueCommit.create(
            self.repo, self.gitcommit, self.issue_tree)
        self.assertEqual(self.gitcommit.hexsha, icommit.hexsha)
        self.assertEqual(self.gitcommit.binsha, icommit.binsha)
        self.assertEqual(len(icommit.issuetree.issues), 6)
        self.assertEqual(icommit.open_issues, 6)


class FindIssuesInCommit(TestCase):

    @classmethod
    def setUpClass(cls):
        safe_create_repo_dir('here')
        cls.repo = IssueRepo()
        cls.repo.issue_dir = 'here'
        cls.repo.issue_objects_dir = 'here/objects'

    def test_commit_contains_no_issues_one_file(self):
        # The magicmock helps to create an iterable object
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

    def test_tree_skips_unicode_error_one_file(self):
        pass

    def test_tree_contains_no_issues_multiple_files(self):
        pass

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
