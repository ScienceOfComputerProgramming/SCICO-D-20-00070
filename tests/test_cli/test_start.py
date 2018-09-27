"""
This module tests the functionality of the cli tracker command.
"""
import sys
from io import StringIO
from unittest import TestCase
from unittest.mock import patch, PropertyMock, Mock
from sciit import IssueRepo
from sciit.cli.init import init
from sciit.cli.tracker import tracker
from sciit.cli import start
from tests.external_resources import remove_existing_repo, safe_create_repo_dir
from tests.test_cli.external_resources import repo, third_sha, third_commit
from sciit.cli.color import CPrint, Color


class TestCLIStartup(TestCase):

    def setUp(self):
        self.held, sys.stdout = sys.stdout, StringIO()

    def test_main_entrance(self):
        CPrint.bold_yellow('test')
        Color.bold_green('test')
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
    @patch('sciit.repo.IssueRepo.build_issue_commits')
    def test_init_command_runs_smoothly(self, build, args):
        val = Mock()
        val.func = init
        val.reset = False
        args.return_value = val
        start.main()
        pass

    @patch('argparse.ArgumentParser.parse_args', new_callable=Mock)
    @patch('sciit.cli.start.IssueRepo')
    def test_tracker_command_error_repo_not_initialized(self, repo, args):
        val = Mock()
        val.func = tracker
        val.reset = False
        args.return_value = val
        remove_existing_repo('there')
        repo.return_value = IssueRepo('there')
        start.main()
        self.assertIn('Repository not initialized', sys.stdout.getvalue())

    @patch('argparse.ArgumentParser.parse_args', new_callable=Mock)
    @patch('sciit.cli.start.IssueRepo')
    @patch('sciit.cli.start.IssueRepo.heads')
    def test_tracker_command_error_no_commits(self, heads, patch_repo, args):
        val = Mock()
        val.func = tracker
        val.reset = False
        val.revision = None
        args.return_value = val
        remove_existing_repo('there')
        repo = IssueRepo('there')
        repo.setup_fs_resources()
        repo.heads = []
        patch_repo.return_value = repo
        start.main()
        self.assertIn('git sciit error fatal:', sys.stdout.getvalue())

    @patch('argparse.ArgumentParser.parse_args', new_callable=Mock)
    @patch('sciit.cli.start.IssueRepo')
    @patch('sciit.cli.start.IssueRepo.heads')
    @patch('sciit.cli.start.IssueRepo.sync')
    def test_tracker_command_error_incomplete_repository(self, sync, heads, patch_repo, args):
        val = Mock()
        val.func = tracker
        val.reset = False
        val.revision = third_sha
        args.return_value = val
        mhead = Mock()
        mhead.commit = third_commit
        mhead.name = 'master'
        repo.heads = [mhead]
        patch_repo.return_value = repo
        start.main()
        self.assertIn(
            'Solve error by rebuilding issue repository using', sys.stdout.getvalue())

    @patch('argparse.ArgumentParser.parse_args', new_callable=Mock)
    @patch('sciit.cli.start.IssueRepo')
    @patch('sciit.cli.start.IssueRepo.heads')
    @patch('sciit.cli.start.IssueRepo.sync')
    def test_tracker_command_error_bad_revision(self, sync, heads, patch_repo, args):
        val = Mock()
        val.func = tracker
        val.reset = False
        val.revision = 'aiansifaisndzzz'
        args.return_value = val
        mhead = Mock()
        mhead.commit = third_commit
        mhead.name = 'master'
        repo.heads = [mhead]
        patch_repo.return_value = repo
        start.main()
        self.assertIn(
            'git sciit error fatal: bad revision', sys.stdout.getvalue())
