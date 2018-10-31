import sys
from io import StringIO
from unittest import TestCase
from unittest.mock import Mock, patch, MagicMock

from sciit.cli.log import log
from tests.test_cli.external_resources import first_commit, first_issue_snapshots, second_commit,\
    second_issue_snapshots


class TestLogCommand(TestCase):

    def setUp(self):
        self.held, sys.stdout = sys.stdout, StringIO()

    @patch('pydoc.pipepager')
    def test_log_generates_correctly_from_two_commits(self, pager):
        args = Mock()
        args.revision = False
        args.repo = MagicMock()
        args.repo.find_issue_snapshots.return_value= first_issue_snapshots + second_issue_snapshots

        args.repo.head = second_commit.hexsha
        output = log(args)
        self.assertIn('commit ' + second_commit.hexsha, output)
        self.assertIn('Open Issue Ids:\n 6\n 5\n 4\n 3\n 2\n 1\n\n', output)
        self.assertIn('commit ' + first_commit.hexsha, output)

    @patch('pydoc.pipepager')
    def test_log_generates_correctly_from_revision(self, pager):
        args = Mock()
        args.revision = second_commit.hexsha
        args.repo = MagicMock()
        args.repo.find_issue_snapshots.return_value= first_issue_snapshots + second_issue_snapshots
        args.repo.head = second_commit.hexsha
        output = log(args)
        self.assertIn('commit ' + second_commit.hexsha, output)
        self.assertIn('Open Issue Ids:\n 6\n 5\n 4\n 3\n 2\n 1\n\n', output)
        self.assertIn('commit ' + first_commit.hexsha, output)
