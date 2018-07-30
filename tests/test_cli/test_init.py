"""
This module tests the functionality of the cli init command.
"""
import sys
from io import StringIO
from unittest import TestCase
from unittest.mock import Mock, patch

from git import Commit
from git.util import hex_to_bin
from sciit import IssueRepo
from sciit.cli.init import init
from tests.external_resources import remove_existing_repo, safe_create_repo_dir


class TestInitRepository(TestCase):

    @classmethod
    def setUpClass(cls):
        first_commit = '43e8d11ec2cb9802151533ae8d9c5dcc5dec91a4'
        second_commit = '622918a4c6539f853320e06804f73d1165df69d0'
        third_commit = '7a13fb71dfc40675176ce28b8ad6df9132039711'
        repo = IssueRepo()
        cls.first_commit = Commit(repo, hex_to_bin(first_commit))
        cls.second_commit = Commit(repo, hex_to_bin(second_commit))
        cls.third_commit = Commit(repo, hex_to_bin(third_commit))

    def setUp(self):
        self.held, sys.stdout = sys.stdout, StringIO()

    @patch('sciit.repo.IssueRepo.heads')
    def test_init_reset(self, heads):
        remove_existing_repo('here')
        args = Mock()
        args.repo = IssueRepo('here')
        args.reset = True
        heads.return_value = []
        init(args)
        self.assertIn('The issue repository is empty.',
                      sys.stdout.getvalue())

    @patch('sciit.repo.IssueRepo.iter_commits')
    def test_init_reset_repo_exists_no_commits(self, commits):
        safe_create_repo_dir('here')
        args = Mock()
        args.repo = IssueRepo('here')
        args.reset = True
        commits.return_value = []
        init(args)
        self.assertIn('Building repository from commits',
                      sys.stdout.getvalue())
        self.assertIn('The repository has no commits',
                      sys.stdout.getvalue())
        self.assertIn('Empty issue repository created',
                      sys.stdout.getvalue())

    @patch('sciit.repo.IssueRepo.iter_commits')
    @patch('sciit.repo.find_issues_in_tree')
    def test_init_reset_repo_exists_with_commits(self, tree, commits):
        safe_create_repo_dir('here')
        args = Mock()
        args.repo = IssueRepo('here')
        args.repo.cli = True
        args.reset = True
        commits.return_value = [self.third_commit,
                                self.second_commit,
                                self.third_commit]
        tree.return_value = []
        init(args)
        self.assertIn('Building repository from commits',
                      sys.stdout.getvalue())
        self.assertIn('3/3 commits:',
                      sys.stdout.getvalue())

    @patch('sciit.repo.IssueRepo.heads')
    def test_init_with_no_commits(self, heads):
        remove_existing_repo('here')
        args = Mock()
        args.repo = IssueRepo('here')
        args.reset = False
        heads.return_value = []
        init(args)
        self.assertIn('Building repository from commits',
                      sys.stdout.getvalue())
        self.assertIn('The repository has no commits',
                      sys.stdout.getvalue())
        self.assertIn('Empty issue repository created',
                      sys.stdout.getvalue())

    def test_init_repo_exists(self):
        safe_create_repo_dir('here')
        args = Mock()
        args.repo = IssueRepo('here')
        args.reset = False
        init(args)
        self.assertIn('Issue repository already setup',
                      sys.stdout.getvalue())
