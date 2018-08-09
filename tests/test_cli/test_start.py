"""
This module tests the functionality of the cli tracker command.
"""
import sys
from io import StringIO
from unittest import TestCase
from unittest.mock import patch, PropertyMock, Mock

from sciit.cli import start


class TestCLIStartup(TestCase):

    def setUp(self):
        self.held, sys.stdout = sys.stdout, StringIO()

    def test_main_entrance(self):
        with patch.object(start, "main", return_value=42):
            with patch.object(start, "__name__", "__main__"):
                with patch.object(start.sys, 'exit') as mock_exit:
                    start.start()
                    assert mock_exit.call_args[0][0] == 42

    @patch('git.repo.base.Repo.git_dir', new_callable=PropertyMock)
    def test_not_in_valid_git_dir(self, path):
        path.return_value = None
        start.main()
        self.assertIn('fatal: not a git repository', sys.stdout.getvalue())
        self.assertIn('Stopping at filesystem boundary', sys.stdout.getvalue())

    def test_no_arguments_supplied(self):
        args = ['command']
        with patch.object(sys, 'argv', args):
            start.main()
            self.assertIn('usage: git sciit [-h] [-v]', sys.stdout.getvalue())

    @patch('argparse.ArgumentParser.parse_args', new_callable=Mock)
    def test_any_command_supplied(self, args):
        args.func = 'Function'
        start.main()

    # def test_command_fails_if_no_issue_repo(self):
    #     args = Mock()
    #     args.repo = IssueRepo('there')
    #     args.issueid = ''
    #     issue(args)
    #     self.assertIn('Repository not initialized',
    #                   sys.stdout.getvalue())

    # @patch('sciit.repo.IssueRepo.sync')
    # def test_command_fails_if_bad_revision(self, sync):
    #     args = Mock()
    #     args.issueid = ''
    #     args.repo = self.repo
    #     args.revision = 'asdfesdasd'
    #     issue(args)
    #     self.assertIn('git sciit error fatal: bad revision ',
    #                   sys.stdout.getvalue())

    # @patch('sciit.repo.IssueRepo.heads')
    # @patch('sciit.repo.IssueRepo.sync')
    # def test_command_fails_if_no_commits(self, sync, heads):
    #     args = Mock()
    #     args.issueid = ''
    #     args.revision = None
    #     args.repo = self.repo
    #     args.normal = args.detailed = args.full = False
    #     args.repo.heads = []

    #     issue(args)
    #     self.assertIn('git sciit error fatal:',
    #                   sys.stdout.getvalue())
    #     self.assertIn('The repository has no commits.',
    #                   sys.stdout.getvalue())

    # @patch('sciit.repo.IssueRepo.heads')
    # @patch('sciit.repo.IssueRepo.sync')
    # def test_command_fails_if_no_commits(self, sync, heads):
    #     args = Mock()
    #     args.revision = self.second
    #     args.repo = self.repo

    #     args.normal = args.detailed = args.full = args.all = args.open = args.save = False
    #     args.closed = True
    #     args.repo.heads = []

    #     tracker(args)
    #     self.assertIn('git sciit error fatal:',
    #                   sys.stdout.getvalue())
    #     self.assertIn('The repository has no commits.',
    #                   sys.stdout.getvalue())
