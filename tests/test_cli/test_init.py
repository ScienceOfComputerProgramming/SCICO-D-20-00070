import sys
from io import StringIO
from unittest import TestCase
from unittest.mock import Mock, patch

from sciit import IssueRepo
from sciit.cli.init import init
from tests.external_resources import remove_existing_repo, safe_create_repo_dir


class TestInitCommand(TestCase):

    def setUp(self):
        self.held, sys.stdout = sys.stdout, StringIO()
        self.mock_args = Mock()
        self.mock_args.repo = IssueRepo('there')

    def tearDown(self):
        remove_existing_repo('there')

    @patch('sciit.repo.IssueRepo.heads')
    def test_init_reset(self, heads):
        self.mock_args.reset = True
        heads.return_value = list()
        init(self.mock_args)

        self.assertIn('The issue repository is empty.', sys.stdout.getvalue())

    @patch('sciit.repo.IssueRepo.iter_commits')
    def test_init_reset_repo_exists_no_commits(self, commits):
        safe_create_repo_dir('there')
        self.mock_args.reset = True
        commits.return_value = list()
        init(self.mock_args)

        self.assertIn('Building repository from commits', sys.stdout.getvalue())
        self.assertIn('The repository has no commits', sys.stdout.getvalue())
        self.assertIn('Empty issue repository created', sys.stdout.getvalue())

    @patch('sciit.repo.IssueRepo.heads')
    def test_init_with_no_commits(self, heads):
        self.mock_args.reset = False
        heads.return_value = list()
        init(self.mock_args)

        self.assertIn('Building repository from commits', sys.stdout.getvalue())
        self.assertIn('The repository has no commits', sys.stdout.getvalue())
        self.assertIn('Empty issue repository created', sys.stdout.getvalue())

    def test_init_repo_exists(self):
        safe_create_repo_dir('there')
        self.mock_args.reset = False
        init(self.mock_args)

        self.assertIn('Issue repository already setup', sys.stdout.getvalue())
