import sys
from io import StringIO
from unittest import TestCase
from unittest.mock import Mock, patch

from sciit.cli.log import log
from tests.test_cli.external_resources import repo, second_sha, first_sha


class TestLogCommand(TestCase):

    def setUp(self):
        self.held, sys.stdout = sys.stdout, StringIO()

    @patch('sciit.repo.IssueRepo.head')
    @patch('sciit.repo.IssueRepo.sync')
    @patch('pydoc.pipepager')
    def test_log_generates_correctly_from_two_commits(self, pager, sync, head):
        args = Mock()
        args.revision = False
        args.repo = repo
        args.repo.head = second_sha
        output = log(args)
        self.assertIn('commit ' + second_sha, output)
        self.assertIn('Open Issues: 5', output)
        self.assertIn('commit ' + first_sha, output)
        self.assertIn('Open Issues: 6', output)

    @patch('sciit.repo.IssueRepo.head')
    @patch('sciit.repo.IssueRepo.sync')
    @patch('pydoc.pipepager')
    def test_log_generates_correctly_from_revision(self, pager, sync, head):
        args = Mock()
        args.revision = second_sha
        args.repo = repo
        args.repo.head = second_sha
        output = log(args)
        self.assertIn('commit ' + second_sha, output)
        self.assertIn('Open Issues: 5', output)
        self.assertIn('commit ' + first_sha, output)
        self.assertIn('Open Issues: 6', output)
