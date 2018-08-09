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
from tests.test_cli.external_resources import second_commit, first_commit


"""
@issue test coverage on error
@title Find a way to test for Keyboard Interrupt Error
@description
    This will help with code coverage
"""


class TestInitCommand(TestCase):

    def setUp(self):
        self.held, sys.stdout = sys.stdout, StringIO()

    @classmethod
    def tearDownClass(cls):
        remove_existing_repo('there')

    @patch('sciit.repo.IssueRepo.heads')
    def test_init_reset(self, heads):
        remove_existing_repo('there')
        args = Mock()
        args.repo = IssueRepo('there')
        args.reset = True
        heads.return_value = []
        init(args)
        self.assertIn('The issue repository is empty.',
                      sys.stdout.getvalue())

    @patch('sciit.repo.IssueRepo.iter_commits')
    def test_init_reset_repo_exists_no_commits(self, commits):
        safe_create_repo_dir('there')
        args = Mock()
        args.repo = IssueRepo('there')
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
    @patch('sciit.repo.find_issues_in_commit')
    def test_init_reset_repo_exists_with_commits(self, issues, commits):
        safe_create_repo_dir('there')
        args = Mock()
        args.repo = IssueRepo('there')
        args.repo.cli = True
        args.reset = True
        commits.return_value = [second_commit,
                                first_commit]
        issues.return_value = []
        init(args)
        self.assertIn('Building repository from commits',
                      sys.stdout.getvalue())
        self.assertIn('2/2 commits:',
                      sys.stdout.getvalue())

    @patch('sciit.repo.IssueRepo.heads')
    def test_init_with_no_commits(self, heads):
        remove_existing_repo('there')
        args = Mock()
        args.repo = IssueRepo('there')
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
        safe_create_repo_dir('there')
        args = Mock()
        args.repo = IssueRepo('there')
        args.reset = False
        init(args)
        self.assertIn('Issue repository already setup',
                      sys.stdout.getvalue())
