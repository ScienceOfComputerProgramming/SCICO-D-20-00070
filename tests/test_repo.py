import sys
import os
import shutil
from unittest import TestCase
from unittest.mock import patch, Mock, PropertyMock, MagicMock
from git import Commit
from git.util import hex_to_bin
from sciit import IssueRepo, IssueCommit, IssueTree, Issue
from sciit.errors import EmptyRepositoryError, NoCommitsError

from tests.external_resources import safe_create_repo_dir, remove_existing_repo


class TestIssueRepoExistingRepository(TestCase):

    def setUp(self):
        safe_create_repo_dir('here')

    def test_issue_repo_is_init(self):
        repo = IssueRepo('here')
        self.assertTrue(repo.is_init())

    def test_reset_init_repo(self):
        repo = IssueRepo('here')
        repo.reset()
        self.assertFalse(os.path.exists('here'))


class TestIssueRepoNoExistingRepository(TestCase):

    def setUp(self):
        remove_existing_repo('here')

    def test_issue_repo_is_not_init(self):
        repo = IssueRepo('here')
        self.assertFalse(repo.is_init())

    def test_issue_repo_setup(self):
        repo = IssueRepo('here')
        repo.setup()
        self.assertTrue(os.path.exists(repo.git_dir + '/hooks/post-commit'))

    def test_reset_non_init_repo(self):
        repo = IssueRepo('here')
        with self.assertRaises(EmptyRepositoryError) as context:
            repo.reset()
        self.assertTrue(
            'The issue repository is empty.' in str(context.exception))


class TestBuildIssueRepo(TestCase):

    def setUp(self):
        safe_create_repo_dir('here')
        self.repo = IssueRepo('here')

    @patch('sciit.repo.IssueRepo.heads', new_callable=PropertyMock)
    def test_build_from_empty_repo(self, heads):
        heads.return_value = []
        with self.assertRaises(NoCommitsError) as context:
            self.repo.build()
        self.assertTrue(
            'The repository has no commits.' in str(context.exception))
        heads.assert_called_once()

    @patch('sciit.repo.IssueRepo.iter_commits')
    def test_build_from_two_known_commits(self, commits):
        # get first two commits of this repo
        first = '43e8d11ec2cb9802151533ae8d9c5dcc5dec91a4'
        second = '622918a4c6539f853320e06804f73d1165df69d0'
        val = [Commit(self.repo, hex_to_bin(second)),
               Commit(self.repo, hex_to_bin(first))]
        commits.return_value = val

        # build
        self.repo.build()
        commits.assert_called_once()

        # check two IssueCommits made with Issue Tree
        first_commit = IssueCommit(self.repo, first)
        second_commit = IssueCommit(self.repo, second)

        # check issues created properly
        self.assertEqual(first_commit.commit, val[1])
        self.assertEqual(second_commit.commit, val[0])
        self.assertEqual(len(first_commit.issuetree.issues), 0)
        self.assertEqual(len(second_commit.issuetree.issues), 0)

    @patch('sciit.repo.IssueRepo.iter_commits')
    @patch('sciit.repo.print_progress_bar')
    def test_print_progress_called_if_cli(self, progress, commits):
        # get first two commits of this repo
        first = '43e8d11ec2cb9802151533ae8d9c5dcc5dec91a4'
        second = '622918a4c6539f853320e06804f73d1165df69d0'
        val = [Commit(self.repo, hex_to_bin(second)),
               Commit(self.repo, hex_to_bin(first))]
        commits.return_value = val

        self.repo.cli = True
        self.repo.build()
        self.assertTrue(progress.called)


class TestBuildIterIssueCommits(TestCase):

    @classmethod
    def setUpClass(cls):
        safe_create_repo_dir('here')
        cls.repo = IssueRepo('here')

        data = [{'id': '1', 'title': 'the contents of the file', 'filepath': 'path'},
                {'id': '2', 'title': 'the contents of the file', 'filepath': 'path'},
                {'id': '3', 'title': 'the contents of the file', 'filepath': 'path'},
                {'id': '4', 'title': 'the contents of the file', 'filepath': 'path'},
                {'id': '5', 'title': 'the contents of the file', 'filepath': 'path'},
                {'id': '6', 'title': 'the contents of the file', 'filepath': 'path',
                 'description': 'here is a nice description'}]

        new_data = [{'id': '1', 'title': 'the contents of the file', 'filepath': 'path'},
                    {'id': '2', 'title': 'the contents of the file', 'filepath': 'path'},
                    {'id': '9', 'title': 'the contents of the file', 'filepath': 'path'}, ]
        cls.issues = []
        cls.new_issues = []
        for d in data:
            cls.issues.append(Issue.create(cls.repo, d))
        cls.itree = IssueTree.create(cls.repo, cls.issues)

        for d in new_data:
            cls.new_issues.append(Issue.create(cls.repo, d))
        cls.new_itree = IssueTree.create(cls.repo, cls.new_issues)

        cls.head = '622918a4c6539f853320e06804f73d1165df69d0'
        cls.first = '43e8d11ec2cb9802151533ae8d9c5dcc5dec91a4'
        cls.head_commit = Commit(cls.repo, hex_to_bin(cls.head))
        cls.first_commit = Commit(cls.repo, hex_to_bin(cls.first))
        cls.head_icommit = IssueCommit.create(
            cls.repo, cls.head_commit, cls.new_itree)
        IssueCommit.create(cls.repo, cls.first_commit, cls.itree)

    @patch('sciit.repo.IssueRepo.iter_commits')
    @patch('sciit.repo.IssueRepo.heads')
    def test_get_build_history(self, heads, commits):
        val = [self.head_commit, self.first_commit]
        commits.return_value = val
        head = MagicMock()
        head.commit = self.head_icommit
        head.name = 'master'
        heads.__iter__.return_value = [head]
        history = self.repo.build_history('--all')
        self.assertEqual(len(history), 7)
        self.assertTrue(
            'here is a nice description' in history['6']['description'])

    @patch('sciit.repo.IssueRepo.heads')
    def test_get_build_history_no_commits(self, heads):
        repo = IssueRepo()
        repo.heads = False
        with self.assertRaises(NoCommitsError) as context:
            repo.build_history('--all')
        self.assertTrue(
            'The repository has no commits.' in str(context.exception))

    @patch('sciit.repo.IssueRepo.iter_commits')
    @patch('sciit.repo.IssueRepo.heads')
    def test_get_open_issues(self, heads, commits):
        val = [self.head_commit, self.first_commit]
        commits.return_value = val
        head = MagicMock()
        head.commit = self.head_icommit
        head.name = 'master'
        heads.__iter__.return_value = [head]
        open_issues = self.repo.open_issues
        self.assertEqual(len(open_issues), 3)

    @patch('sciit.repo.IssueRepo.iter_commits')
    @patch('sciit.repo.IssueRepo.heads')
    def test_get_all_issues(self, heads, commits):
        val = [self.head_commit, self.first_commit]
        commits.return_value = val
        head = MagicMock()
        head.commit = self.head_icommit
        head.name = 'master'
        heads.__iter__.return_value = [head]
        all_issues = self.repo.all_issues
        self.assertEqual(len(all_issues), 7)

    @patch('sciit.repo.IssueRepo.iter_commits')
    @patch('sciit.repo.IssueRepo.heads')
    def test_get_closed_issues(self, heads, commits):
        val = [self.head_commit, self.first_commit]
        commits.return_value = val
        head = MagicMock()
        head.commit = self.head_icommit
        head.name = 'master'
        heads.__iter__.return_value = [head]
        closed_issues = self.repo.closed_issues
        self.assertEqual(len(closed_issues), 4)


class TestIssueStatus(TestCase):

    def setUp(self):
        safe_create_repo_dir('here')
        self.repo = IssueRepo('here')

    @patch('sciit.repo.IssueRepo.iter_commits')
    def test_return_two_known_issue_commits(self, iter_commits):
        # get first two commits of this repo
        first = '43e8d11ec2cb9802151533ae8d9c5dcc5dec91a4'
        second = '622918a4c6539f853320e06804f73d1165df69d0'
        val = [Commit(self.repo, hex_to_bin(second)),
               Commit(self.repo, hex_to_bin(first))]
        iter_commits.return_value = val

        data = {'id': '1', 'title': 'hello world', 'filepath': 'README.md'}
        issue = Issue.create(self.repo, data)
        itree = IssueTree.create(self.repo, [issue])
        IssueCommit.create(self.repo, val[1], itree)
        IssueCommit.create(self.repo, val[0], itree)

        icommits = list(self.repo.iter_issue_commits('--all'))

        self.assertEqual(icommits[1].hexsha, val[1].hexsha)
        self.assertEqual(icommits[0].hexsha, val[0].hexsha)
