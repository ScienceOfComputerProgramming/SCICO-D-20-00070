import sys
from io import StringIO
from unittest import TestCase
from unittest.mock import Mock

from sciit import IssueRepo
from sciit.cli.init import init
from tests.external_resources import remove_existing_repo, create_mock_git_repository


class TestInitCommand(TestCase):

    def setUp(self):
        self.held, sys.stdout = sys.stdout, StringIO()
        self.mock_args = Mock()
        mock_git_repository = create_mock_git_repository('there', list(), list())

        self.mock_args.repo = IssueRepo(mock_git_repository)

    def test_init_reset(self):
        self.mock_args.reset = True
        init(self.mock_args)
        self.assertIn('The issue repository is empty.', sys.stdout.getvalue())

    def tearDown(self):
        remove_existing_repo('there')

    def test_init_reset_repo_exists_no_commits(self):
        self.mock_args.reset = True
        self.mock_args.repo.setup_file_system_resources()
        init(self.mock_args)

        self.assertIn('Building repository from commits', sys.stdout.getvalue())
        self.assertIn('The repository has no commits', sys.stdout.getvalue())
        self.assertIn('Empty issue repository created', sys.stdout.getvalue())

    def test_init_with_no_commits(self):
        self.mock_args.reset = False
        init(self.mock_args)

        self.assertIn('Building repository from commits', sys.stdout.getvalue())
        self.assertIn('The repository has no commits', sys.stdout.getvalue())
        self.assertIn('Empty issue repository created', sys.stdout.getvalue())

    def  test_init_repo_exists(self):
        self.mock_args.reset = False
        self.mock_args.repo.setup_file_system_resources()
        init(self.mock_args)

        self.assertIn('Issue repository already setup', sys.stdout.getvalue())
