import sys
from io import StringIO
from unittest import TestCase
from unittest.mock import patch, PropertyMock, Mock, MagicMock

from git import GitCommandError

from sciit import IssueRepo
from sciit.cli.init import init
from sciit.cli.tracker import tracker
from sciit.cli import start
from sciit.errors import RepoObjectDoesNotExistError, NoCommitsError
from tests.external_resources import remove_existing_repo
from tests.test_cli.external_resources import third_commit
from sciit.cli.color import CPrint, Color


class TestCLIStartup(TestCase):

    def setUp(self):
        self.held, sys.stdout = sys.stdout, StringIO()

    def test_main_entrance(self):
        CPrint.bold_yellow('test')
        Color.bold_green('test')
        with \
                patch.object(start, "main", return_value=42), \
                patch.object(start, "__name__", "__main__"),\
                patch.object(start.sys, 'exit') as mock_exit:
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
    def test_init_command_runs_smoothly(self, parse_args):
        args = Mock()
        args.return_value = Mock()
        args.func = init
        args.reset = False
        parse_args.return_value = args

        start.main()

    @patch('argparse.ArgumentParser.parse_args', new_callable=Mock)
    @patch('sciit.cli.start.IssueRepo.is_init', new_callable=MagicMock)
    def test_tracker_command_error_repo_not_initialized(self, is_init, parse_args):

        args = Mock()
        args.func = tracker
        args.reset = False
        is_init.return_value=False
        parse_args.return_value = args

        start.main()
        self.assertIn('Repository not initialized', sys.stdout.getvalue())

    @patch('argparse.ArgumentParser.parse_args', new_callable=Mock)
    @patch('sciit.cli.start.IssueRepo')
    def test_tracker_command_error_no_commits(self, patch_repo, args):
        val = Mock()
        val.func = tracker
        val.reset = False
        val.revision = None
        args.return_value = val
        repo = Mock()
        repo.heads = []
        patch_repo.return_value = repo

        repo.get_open_issues.side_effect = NoCommitsError()

        start.main()
        self.assertIn('git sciit error fatal:', sys.stdout.getvalue())

    @patch('argparse.ArgumentParser.parse_args', new_callable=Mock)
    @patch('sciit.cli.start.IssueRepo')
    def test_tracker_command_error_incomplete_repository(self, patch_repo, args):
        val = Mock()
        val.func = tracker
        val.reset = False
        val.revision = third_commit.hexsha
        args.return_value = val
        mock_head = Mock()
        mock_head.commit = third_commit
        mock_head.name = 'master'
        repo = Mock()
        repo.heads = [mock_head]

        repo.get_open_issues.side_effect = RepoObjectDoesNotExistError('there')

        patch_repo.return_value = repo
        start.main()
        self.assertIn('Solve error by rebuilding issue repository using', sys.stdout.getvalue())

    @patch('argparse.ArgumentParser.parse_args', new_callable=Mock)
    @patch('sciit.cli.start.IssueRepo.is_init', new_callable=MagicMock)
    @patch('sciit.cli.start.IssueRepo.get_open_issues', new_callable=MagicMock)
    def test_tracker_command_error_bad_revision(self, get_open_issues, is_init, parse_args):
        args_mock = MagicMock()
        args_mock.func = tracker
        args_mock.reset = False
        args_mock.open = True

        args_mock.revision = 'aiansifaisndzzz'

        parse_args.return_value = args_mock

        is_init.return_value=True
        get_open_issues.side_effect=GitCommandError('xy', 'xx')
        start.main()
        self.assertIn('git sciit error fatal: bad revision', sys.stdout.getvalue())
