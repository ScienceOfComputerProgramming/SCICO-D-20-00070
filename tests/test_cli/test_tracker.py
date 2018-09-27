"""
This module tests the functionality of the cli tracker command.
"""
import sys
from io import StringIO
from unittest import TestCase
from unittest.mock import Mock, patch

from sciit.cli.tracker import tracker
from tests.test_cli.external_resources import repo, second_sha, second_commit, ansi_escape


class TestStatusCommand(TestCase):

    def setUp(self):
        self.held, sys.stdout = sys.stdout, StringIO()

    @patch('sciit.repo.IssueRepo.build_history')
    @patch('sciit.repo.IssueRepo.heads')
    @patch('sciit.repo.IssueRepo.sync')
    def test_command_finds_no_history(self, sync, heads, history):
        args = Mock()
        args.revision = second_sha
        args.repo = repo

        args.all = True
        args.normal = args.detailed = args.full = args.open = args.closed = args.save = False
        args.repo.heads = []
        args.repo.build_history.return_value = {}

        tracker(args)
        self.assertIn('No issues found', sys.stdout.getvalue())

    @patch('sciit.repo.IssueRepo.heads')
    @patch('sciit.repo.IssueRepo.sync')
    @patch('pydoc.pipepager')
    def test_prints_correct_tracker_info(self, pager, sync, heads):
        args = Mock()
        args.revision = second_sha
        args.repo = repo

        args.all = args.closed = args.save = args.normal = args.detailed = args.full = False
        args.open = True

        mhead = Mock()
        mhead.commit = second_commit
        mhead.name = 'master'
        args.repo.heads = [mhead]

        output = tracker(args)
        output = ansi_escape.sub('', output)
        self.assertIn('ID: 6\nStatus: Open', output)

    @patch('sciit.repo.IssueRepo.heads')
    @patch('sciit.repo.IssueRepo.sync')
    @patch('pydoc.pipepager')
    def test_prints_correct_tracker_info_default(self, pager, sync, heads):
        args = Mock()
        args.revision = second_sha
        args.repo = repo

        args.normal = args.detailed = args.full = False
        args.closed = args.save = args.open = args.all = False

        mhead = Mock()
        mhead.commit = second_commit
        mhead.name = 'master'
        args.repo.heads = [mhead]

        output = tracker(args)
        output = ansi_escape.sub('', output)
        self.assertIn('ID: 2\nStatus: Open', output)
        self.assertIn('ID: 9\nStatus: Open', output)

    @patch('sciit.repo.IssueRepo.heads')
    @patch('sciit.repo.IssueRepo.sync')
    @patch('pydoc.pipepager')
    def test_prints_correct_tracker_info_all(self, pager, sync, heads):
        args = Mock()
        args.revision = second_sha
        args.repo = repo

        args.all = True
        args.open = args.normal = args.detailed = args.full = args.closed = args.save = False

        mhead = Mock()
        mhead.commit = second_commit
        mhead.name = 'master'
        args.repo.heads = [mhead]

        output = tracker(args)
        output = ansi_escape.sub('', output)
        self.assertIn('ID: 5\nStatus: Closed', output)
        self.assertIn('ID: 4\nStatus: Closed', output)
        self.assertIn('ID: 3\nStatus: Closed', output)
        self.assertIn('ID: 9\nStatus: Open', output)
        self.assertIn('ID: 6\nStatus: Open', output)

    @patch('sciit.repo.IssueRepo.heads')
    @patch('sciit.repo.IssueRepo.sync')
    @patch('pydoc.pipepager')
    def test_prints_correct_tracker_info_closed(self, pager, sync, heads):
        args = Mock()
        args.revision = second_sha
        args.repo = repo

        args.all = args.normal = args.detailed = args.full = args.save = args.open = False
        args.closed = True

        mhead = Mock()
        mhead.commit = second_commit
        mhead.name = 'master'
        args.repo.heads = [mhead]

        output = tracker(args)
        output = ansi_escape.sub('', output)
        self.assertIn('ID: 5\nStatus: Closed', output)
        self.assertIn('ID: 4\nStatus: Closed', output)
        self.assertIn('ID: 3\nStatus: Closed', output)
        self.assertNotIn('ID: 9\nStatus: Open', output)

    @patch('sciit.repo.IssueRepo.heads')
    @patch('sciit.repo.IssueRepo.sync')
    @patch('pydoc.pipepager')
    def test_prints_correct_tracker_info_and_saves(self, pager, sync, heads):
        args = Mock()
        args.revision = second_sha
        args.repo = repo

        args.all = args.normal = args.detailed = args.full = args.closed = False
        args.open = args.save = True

        mhead = Mock()
        mhead.commit = second_commit
        mhead.name = 'master'
        args.repo.heads = [mhead]

        output = tracker(args)
        self.assertIsNone(output)

    @patch('sciit.repo.IssueRepo.heads')
    @patch('sciit.repo.IssueRepo.sync')
    @patch('pydoc.pipepager')
    def test_prints_normal_tracker_view(self, pager, sync, heads):
        args = Mock()
        args.revision = second_sha
        args.repo = repo

        args.open = args.save = args.detailed = args.full = args.closed = False
        args.all = args.normal = True

        mhead = Mock()
        mhead.commit = second_commit
        mhead.name = 'master'
        args.repo.heads = [mhead]

        output = tracker(args)
        output = ansi_escape.sub('', output)
        self.assertNotIn('Descriptions:', output)
        self.assertNotIn('File paths:', output)
        self.assertNotIn('Commit Activities:', output)
        self.assertNotIn('Found In:', output)
        self.assertNotIn('Open In Branches:', output)

    @patch('sciit.repo.IssueRepo.heads')
    @patch('sciit.repo.IssueRepo.sync')
    @patch('pydoc.pipepager')
    def test_prints_detailed_tracker_view(self, pager, sync, heads):
        args = Mock()
        args.revision = second_sha
        args.repo = repo

        args.open = args.save = args.normal = args.full = args.closed = False
        args.all = args.detailed = True

        mhead = Mock()
        mhead.commit = second_commit
        mhead.name = 'master'
        args.repo.heads = [mhead]

        output = tracker(args)
        output = ansi_escape.sub('', output)
        self.assertIn('Description:', output)
        self.assertIn('File paths:', output)
        self.assertIn('Commit Activities:', output)
        self.assertIn('Found In:', output)
        self.assertIn('Open In Branches:', output)
        self.assertNotIn('Issue Revisions:', output)

    @patch('sciit.repo.IssueRepo.heads')
    @patch('sciit.repo.IssueRepo.sync')
    @patch('pydoc.pipepager')
    def test_prints_full_tracker_view(self, pager, sync, heads):
        args = Mock()
        args.revision = second_sha
        args.repo = repo

        args.open = args.save = args.normal = args.detailed = args.closed = False
        args.all = args.full = True

        mhead = Mock()
        mhead.commit = second_commit
        mhead.name = 'master'
        args.repo.heads = [mhead]

        output = tracker(args)
        output = ansi_escape.sub('', output)
        self.assertIn('Descriptions:', output)
        self.assertIn('File paths:', output)
        self.assertIn('Commit Activities:', output)
        self.assertIn('Found In:', output)
        self.assertIn('Open In Branches:', output)
        self.assertIn('Issue Revisions:', output)
