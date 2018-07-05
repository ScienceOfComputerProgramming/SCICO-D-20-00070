import sys
import os
import shutil
from unittest import TestCase
from unittest.mock import patch, Mock, PropertyMock, MagicMock
from git import Commit
from git.util import hex_to_bin
from gitissue import IssueRepo, IssueCommit
from gitissue.errors import EmptyRepositoryError, NoCommitsError


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
        repo.setup()
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
        self.repo.setup()

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
    @patch('gitissue.tools.print_progress_bar')
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
