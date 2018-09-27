import sys
from io import StringIO
from unittest import TestCase
from unittest.mock import Mock, patch

from sciit.cli.status import status
from tests.test_cli.external_resources import repo, second_sha, second_commit


class TestStatusCommand(TestCase):

    def setUp(self):
        self.held, sys.stdout = sys.stdout, StringIO()

    @patch('sciit.repo.IssueRepo.heads')
    @patch('sciit.repo.IssueRepo.head')
    @patch('sciit.repo.IssueRepo.sync')
    def test_prints_correct_status_info(self, sync, head, heads):
        args = Mock()
        args.revision = False
        args.repo = repo
        args.repo.head = second_sha
        mhead = Mock()
        mhead.commit = second_commit
        mhead.name = 'master'
        args.repo.heads = [mhead]
        status(args)
        self.assertIn('Open Issues: 5', sys.stdout.getvalue())
        self.assertIn('Closed Issues: 3', sys.stdout.getvalue())

    @patch('sciit.repo.IssueRepo.heads')
    @patch('sciit.repo.IssueRepo.sync')
    def test_prints_correct_status_info_with_revision(self, sync, heads):
        args = Mock()
        args.revision = second_sha
        args.repo = repo
        mhead = Mock()
        mhead.commit = second_commit
        mhead.name = 'master'
        args.repo.heads = [mhead]
        status(args)
        self.assertIn('Open Issues: 5', sys.stdout.getvalue())
        self.assertIn('Closed Issues: 3', sys.stdout.getvalue())