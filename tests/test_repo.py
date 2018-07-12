import sys
import os
import shutil
from unittest import TestCase
from unittest.mock import patch, Mock, PropertyMock, MagicMock
from git import Commit
from git.util import hex_to_bin
from gitissue import IssueRepo, IssueCommit, IssueTree, Issue
from gitissue.errors import EmptyRepositoryError, NoCommitsError
from gitissue.repo import get_open_issues, get_all_issues, get_closed_issues


class TestIssueRepo(TestCase):

    def test_issue_repo_is_init(self):
        if not os.path.exists('here'):
            os.makedirs('here')
            os.makedirs('here/objects')
        repo = IssueRepo()
        repo.issue_dir = 'here'
        repo.issue_objects_dir = 'here/objects'
        self.assertTrue(repo.is_init())

    def test_issue_repo_is_not_init(self):
        repo = IssueRepo()
        repo.issue_dir = 'here'
        repo.issue_objects_dir = 'here/objects'
        self.assertFalse(repo.is_init())

    def test_reset_init_repo(self):
        if not os.path.exists('here'):
            os.makedirs('here')
            os.makedirs('here/objects')
        repo = IssueRepo()
        repo.issue_dir = 'here'
        repo.issue_objects_dir = 'here/objects'
        repo.reset()
        self.assertFalse(os.path.exists('here'))

    def test_reset_non_init_repo(self):
        repo = IssueRepo()
        repo.issue_dir = 'here'
        repo.issue_objects_dir = 'here/objects'
        with self.assertRaises(EmptyRepositoryError) as context:
            repo.reset()
        self.assertTrue(
            'The issue repository is empty.' in str(context.exception))

    def test_repo_setup_correctly(self):
        repo = IssueRepo()
        repo.issue_dir = 'here'
        repo.issue_objects_dir = 'here/objects'
        os.makedirs('here')
        os.makedirs('here/objects')
        self.assertTrue(os.path.exists('here'))
        self.assertTrue(os.path.exists('here/objects'))

    def tearDown(self):
        if os.path.exists('here'):
            shutil.rmtree('here')


class TestBuildIssueRepo(TestCase):

    def setUp(self):
        self.repo = IssueRepo()
        self.repo.issue_dir = 'here'
        self.repo.issue_objects_dir = 'here/objects'
        os.makedirs('here')
        os.makedirs('here/objects')

    @patch('gitissue.repo.IssueRepo.heads', new_callable=PropertyMock)
    def test_build_from_empty_repo(self, heads):
        heads.return_value = []
        with self.assertRaises(NoCommitsError) as context:
            self.repo.build()
        self.assertTrue(
            'The repository has no commits.' in str(context.exception))
        heads.assert_called_once()

    @patch('gitissue.repo.IssueRepo.iter_commits')
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

    @patch('gitissue.repo.IssueRepo.iter_commits')
    @patch('gitissue.repo.print_progress_bar')
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
        pass

    def tearDown(self):
        if os.path.exists('here'):
            shutil.rmtree('here')


class TestBuildIterIssueCommits(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.repo = IssueRepo()
        cls.repo.issue_dir = 'here'
        cls.repo.issue_objects_dir = 'here/objects'
        os.makedirs('here')
        os.makedirs('here/objects')
        data = [{'number': '1', 'description': 'the contents of the file'},
                {'number': '2', 'description': 'the contents of the file'},
                {'number': '3', 'description': 'the contents of the file'},
                {'number': '4', 'description': 'the contents of the file'},
                {'number': '5', 'description': 'the contents of the file'},
                {'number': '6', 'description': 'the contents of the file'}]

        new_data = [{'number': '1', 'description': 'the contents of the file'},
                    {'number': '2', 'description': 'the contents of the file'},
                    {'number': '9', 'description': 'the contents of the file'}, ]
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
        IssueCommit.create(cls.repo, cls.head_commit, cls.new_itree)
        IssueCommit.create(cls.repo, cls.first_commit, cls.itree)

    @patch('gitissue.repo.IssueRepo', autospec=True)
    def test_get_open_issues_branch_none(self, mock_repo):
        mock_repo.head.commit.hexsha = self.head
        mock_repo.issue_dir = 'here'
        mock_repo.issue_objects_dir = 'here/objects'
        open_issues = get_open_issues(mock_repo)
        self.assertEqual(len(open_issues), 3)
        self.assertTrue(hasattr(open_issues[0], 'status'))
        self.assertEqual(open_issues[2].status, 'Open')

    @patch('gitissue.repo.IssueRepo', autospec=True)
    def test_get_open_issues_branch_specified(self, mock_repo):
        branch = 'branch-used-to-update'
        mock_repo.heads[branch].commit.hexsha = self.head
        mock_repo.issue_dir = 'here'
        mock_repo.issue_objects_dir = 'here/objects'
        open_issues = get_open_issues(mock_repo, branch)
        self.assertEqual(len(open_issues), 3)
        self.assertTrue(hasattr(open_issues[0], 'status'))
        self.assertEqual(open_issues[2].status, 'Open')

    @patch('gitissue.repo.IssueRepo', autospec=True)
    def test_get_all_issues(self, mock_repo):
        mock_repo.head.commit.hexsha = self.head
        mock_repo.issue_dir = 'here'
        mock_repo.issue_objects_dir = 'here/objects'
        all_issues = get_all_issues(mock_repo)
        self.assertEqual(len(all_issues), 7)
        self.assertTrue(hasattr(all_issues[0], 'status'))
        self.assertEqual(all_issues[0].status, 'Open')
        self.assertEqual(all_issues[1].status, 'Open')
        self.assertEqual(all_issues[2].status, 'Closed')

    @patch('gitissue.repo.IssueRepo', autospec=True)
    def test_get_closed_issues(self, mock_repo):
        mock_repo.head.commit.hexsha = self.head
        mock_repo.issue_dir = 'here'
        mock_repo.issue_objects_dir = 'here/objects'
        closed_issues = get_closed_issues(mock_repo)
        self.assertEqual(len(closed_issues), 4)
        self.assertTrue(hasattr(closed_issues[0], 'status'))
        self.assertEqual(closed_issues[2].status, 'Closed')

    @classmethod
    def tearDownClass(cls):
        if os.path.exists('here'):
            shutil.rmtree('here')


class TestIssueStatus(TestCase):

    def setUp(self):
        self.repo = IssueRepo()
        self.repo.issue_dir = 'here'
        self.repo.issue_objects_dir = 'here/objects'
        os.makedirs('here')
        os.makedirs('here/objects')

    @patch('gitissue.repo.IssueRepo.iter_commits')
    def test_return_two_known_issue_commits(self, iter_commits):
        # get first two commits of this repo
        first = '43e8d11ec2cb9802151533ae8d9c5dcc5dec91a4'
        second = '622918a4c6539f853320e06804f73d1165df69d0'
        val = [Commit(self.repo, hex_to_bin(second)),
               Commit(self.repo, hex_to_bin(first))]
        iter_commits.return_value = val

        data = {'number': '1', 'filepath': 'README.md'}
        issue = Issue.create(self.repo, data)
        itree = IssueTree.create(self.repo, [issue])
        IssueCommit.create(self.repo, val[1], itree)
        IssueCommit.create(self.repo, val[0], itree)

        icommits = list(self.repo.iter_issue_commits('--all'))

        self.assertEqual(icommits[1].hexsha, val[1].hexsha)
        self.assertEqual(icommits[0].hexsha, val[0].hexsha)

    def tearDown(self):
        if os.path.exists('here'):
            shutil.rmtree('here')
