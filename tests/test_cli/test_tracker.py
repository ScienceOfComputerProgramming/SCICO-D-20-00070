"""
This module tests the functionality of the cli tracker command.
"""
import sys
import re
from io import StringIO
from unittest import TestCase
from unittest.mock import Mock, patch

from git import Commit
from git.util import hex_to_bin
from sciit import IssueRepo, IssueCommit, IssueTree, Issue
from sciit.cli.tracker import tracker
from sciit.functions import write_last_issue
from tests.external_resources import safe_create_repo_dir


class TestStatusCommand(TestCase):

    @classmethod
    def setUpClass(cls):
        safe_create_repo_dir('here')
        cls.repo = IssueRepo('here')
        cls.ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

        data = [{'id': '1', 'title': 'the contents of the file', 'filepath': 'path',
                 'description': 'This issue had a description'},
                {'id': '2', 'title': 'the contents of the file', 'filepath': 'path'},
                {'id': '3', 'title': 'the contents of the file', 'filepath': 'path'},
                {'id': '4', 'title': 'the contents of the file', 'filepath': 'path'},
                {'id': '5', 'title': 'the contents of the file', 'filepath': 'path'},
                {'id': '6',
                 'title': 'The title of your issue',
                 'description': 'A description of you issue as you\n'
                 + 'want it to be ``markdown`` supported',
                 'assignees': 'nystrome, kevin, daniels',
                 'due_date': '12 oct 2018',
                 'label': 'in-development',
                 'weight': '4',
                 'priority': 'high',
                 'filepath': 'README.md'}]

        new_data = [{'id': '1', 'title': 'the contents of the file', 'filepath': 'path'},
                    {'id': '2', 'title': 'the contents of the file', 'filepath': 'path'},
                    {'id': '9', 'title': 'the contents of the file', 'filepath': 'path'},
                    {'id': '6', 'title': 'the contents of the file', 'filepath': 'path',
                     'description': 'description has changed'},
                    {'id': '12', 'title': 'the contents of the file', 'filepath': 'path',
                     'description': 'here is a nice description'}]

        cls.issues = []
        cls.new_issues = []
        for d in data:
            cls.issues.append(Issue.create(cls.repo, d))
        cls.itree = IssueTree.create(cls.repo, cls.issues)

        for d in new_data:
            cls.new_issues.append(Issue.create(cls.repo, d))
        cls.new_itree = IssueTree.create(cls.repo, cls.new_issues)

        cls.second = '622918a4c6539f853320e06804f73d1165df69d0'
        cls.first = '43e8d11ec2cb9802151533ae8d9c5dcc5dec91a4'
        cls.second_commit = Commit(cls.repo, hex_to_bin(cls.second))
        cls.first_commit = Commit(cls.repo, hex_to_bin(cls.first))
        cls.second_icommit = IssueCommit.create(
            cls.repo, cls.second_commit, cls.new_itree)
        cls.first_icommit = IssueCommit.create(
            cls.repo, cls.first_commit, cls.itree)
        write_last_issue(cls.repo.issue_dir, cls.second)

    def setUp(self):
        self.held, sys.stdout = sys.stdout, StringIO()

    def test_command_fails_if_no_issue_repo(self):
        args = Mock()
        args.repo = IssueRepo('there')
        tracker(args)
        self.assertIn('Repository not initialized',
                      sys.stdout.getvalue())

    @patch('sciit.repo.IssueRepo.sync')
    def test_command_fails_if_bad_revision(self, sync):
        args = Mock()
        args.repo = self.repo
        args.revision = 'asdfesdasd'
        tracker(args)
        self.assertIn('git sciit error fatal: bad revision ',
                      sys.stdout.getvalue())

    @patch('sciit.repo.IssueRepo.heads')
    @patch('sciit.repo.IssueRepo.sync')
    def test_command_fails_if_no_commits(self, sync, heads):
        args = Mock()
        args.revision = self.second
        args.repo = self.repo

        args.normal = args.detailed = args.full = args.all = args.open = args.save = False
        args.closed = True
        args.repo.heads = []

        tracker(args)
        self.assertIn('git sciit error fatal:',
                      sys.stdout.getvalue())
        self.assertIn('The repository has no commits.',
                      sys.stdout.getvalue())

    @patch('sciit.repo.IssueRepo.build_history')
    @patch('sciit.repo.IssueRepo.heads')
    @patch('sciit.repo.IssueRepo.sync')
    def test_command_finds_no_history(self, sync, heads, history):
        args = Mock()
        args.revision = self.second
        args.repo = self.repo

        args.all = True
        args.normal = args.detailed = args.full = args.open = args.closed = args.save = False
        args.repo.heads = []
        args.repo.build_history.return_value = {}

        tracker(args)
        self.assertIn('No issues found',
                      sys.stdout.getvalue())

    @patch('sciit.repo.IssueRepo.heads')
    @patch('sciit.repo.IssueRepo.sync')
    @patch('pydoc.pipepager')
    def test_prints_correct_tracker_info(self, pager, sync, heads):
        args = Mock()
        args.revision = self.second
        args.repo = self.repo

        args.all = args.closed = args.save = args.normal = args.detailed = args.full = False
        args.open = True

        mhead = Mock()
        mhead.commit = self.second_commit
        mhead.name = 'master'
        args.repo.heads = [mhead]

        output = tracker(args)
        output = self.ansi_escape.sub('', output)
        self.assertIn('ID: 6\nStatus: Open', output)

    @patch('sciit.repo.IssueRepo.heads')
    @patch('sciit.repo.IssueRepo.sync')
    @patch('pydoc.pipepager')
    def test_prints_correct_tracker_info_default(self, pager, sync, heads):
        args = Mock()
        args.revision = self.second
        args.repo = self.repo

        args.normal = args.detailed = args.full = False
        args.closed = args.save = args.open = args.all = False

        mhead = Mock()
        mhead.commit = self.second_commit
        mhead.name = 'master'
        args.repo.heads = [mhead]

        output = tracker(args)
        output = self.ansi_escape.sub('', output)
        self.assertIn('ID: 2\nStatus: Open', output)
        self.assertIn('ID: 9\nStatus: Open', output)

    @patch('sciit.repo.IssueRepo.heads')
    @patch('sciit.repo.IssueRepo.sync')
    @patch('pydoc.pipepager')
    def test_prints_correct_tracker_info_all(self, pager, sync, heads):
        args = Mock()
        args.revision = self.second
        args.repo = self.repo

        args.all = True
        args.open = args.normal = args.detailed = args.full = args.closed = args.save = False

        mhead = Mock()
        mhead.commit = self.second_commit
        mhead.name = 'master'
        args.repo.heads = [mhead]

        output = tracker(args)
        output = self.ansi_escape.sub('', output)
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
        args.revision = self.second
        args.repo = self.repo

        args.all = args.normal = args.detailed = args.full = args.save = args.open = False
        args.closed = True

        mhead = Mock()
        mhead.commit = self.second_commit
        mhead.name = 'master'
        args.repo.heads = [mhead]

        output = tracker(args)
        output = self.ansi_escape.sub('', output)
        self.assertIn('ID: 5\nStatus: Closed', output)
        self.assertIn('ID: 4\nStatus: Closed', output)
        self.assertIn('ID: 3\nStatus: Closed', output)
        self.assertNotIn('ID: 9\nStatus: Open', output)

    @patch('sciit.repo.IssueRepo.heads')
    @patch('sciit.repo.IssueRepo.sync')
    @patch('pydoc.pipepager')
    def test_prints_correct_tracker_info_and_saves(self, pager, sync, heads):
        args = Mock()
        args.revision = self.second
        args.repo = self.repo

        args.all = args.normal = args.detailed = args.full = args.closed = False
        args.open = args.save = True

        mhead = Mock()
        mhead.commit = self.second_commit
        mhead.name = 'master'
        args.repo.heads = [mhead]

        output = tracker(args)
        self.assertIsNone(output)

    @patch('sciit.repo.IssueRepo.heads')
    @patch('sciit.repo.IssueRepo.sync')
    @patch('pydoc.pipepager')
    def test_prints_normal_tracker_view(self, pager, sync, heads):
        args = Mock()
        args.revision = self.second
        args.repo = self.repo

        args.open = args.save = args.detailed = args.full = args.closed = False
        args.all = args.normal = True

        mhead = Mock()
        mhead.commit = self.second_commit
        mhead.name = 'master'
        args.repo.heads = [mhead]

        output = tracker(args)
        output = self.ansi_escape.sub('', output)
        self.assertNotIn('Descriptions:', output)
        self.assertNotIn('Filepaths:', output)
        self.assertNotIn('Commit Activities:', output)
        self.assertNotIn('Found In:', output)
        self.assertNotIn('Open In Branches:', output)

    @patch('sciit.repo.IssueRepo.heads')
    @patch('sciit.repo.IssueRepo.sync')
    @patch('pydoc.pipepager')
    def test_prints_detailed_tracker_view(self, pager, sync, heads):
        args = Mock()
        args.revision = self.second
        args.repo = self.repo

        args.open = args.save = args.normal = args.full = args.closed = False
        args.all = args.detailed = True

        mhead = Mock()
        mhead.commit = self.second_commit
        mhead.name = 'master'
        args.repo.heads = [mhead]

        output = tracker(args)
        output = self.ansi_escape.sub('', output)
        self.assertIn('Description:', output)
        self.assertIn('Filepaths:', output)
        self.assertIn('Commit Activities:', output)
        self.assertIn('Found In:', output)
        self.assertIn('Open In Branches:', output)
        self.assertNotIn('Issue Revisions:', output)

    @patch('sciit.repo.IssueRepo.heads')
    @patch('sciit.repo.IssueRepo.sync')
    @patch('pydoc.pipepager')
    def test_prints_full_tracker_view(self, pager, sync, heads):
        args = Mock()
        args.revision = self.second
        args.repo = self.repo

        args.open = args.save = args.normal = args.detailed = args.closed = False
        args.all = args.full = True

        mhead = Mock()
        mhead.commit = self.second_commit
        mhead.name = 'master'
        args.repo.heads = [mhead]

        output = tracker(args)
        output = self.ansi_escape.sub('', output)
        self.assertIn('Descriptions:', output)
        self.assertIn('Filepaths:', output)
        self.assertIn('Commit Activities:', output)
        self.assertIn('Found In:', output)
        self.assertIn('Open In Branches:', output)
        self.assertIn('Issue Revisions:', output)
