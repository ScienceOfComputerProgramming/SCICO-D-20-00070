"""
This module tests the functionality of the cli issue command.
"""
import sys
import re
from io import StringIO
from unittest import TestCase
from unittest.mock import Mock, patch

from git import Commit
from git.util import hex_to_bin
from sciit import IssueRepo, IssueCommit, IssueTree, Issue
from sciit.cli.issue import issue
from sciit.functions import write_last_issue
from tests.external_resources import safe_create_repo_dir


class TestStatusCommand(TestCase):

    @classmethod
    def setUpClass(cls):
        safe_create_repo_dir('here')
        cls.repo = IssueRepo('here')
        cls.ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

        new_data = [{'id': '1', 'title': 'the contents of the file', 'filepath': 'path'},
                    {'id': '2', 'title': 'the contents of the file', 'filepath': 'path'},
                    {'id': '9', 'title': 'the contents of the file', 'filepath': 'path'},
                    {'id': '6', 'title': 'the contents of the file', 'filepath': 'path',
                     'description': 'description has changed'},
                    {'id': '12', 'title': 'the contents of the file', 'filepath': 'path',
                     'description': 'here is a nice description'}]

        cls.issues = []
        cls.new_issues = []
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
        args.issueid = ''
        issue(args)
        self.assertIn('Repository not initialized',
                      sys.stdout.getvalue())

    @patch('sciit.repo.IssueRepo.sync')
    def test_command_fails_if_bad_revision(self, sync):
        args = Mock()
        args.issueid = ''
        args.repo = self.repo
        args.revision = 'asdfesdasd'
        issue(args)
        self.assertIn('git sciit error fatal: bad revision ',
                      sys.stdout.getvalue())

    @patch('sciit.repo.IssueRepo.heads')
    @patch('sciit.repo.IssueRepo.sync')
    def test_command_fails_if_no_commits(self, sync, heads):
        args = Mock()
        args.issueid = ''
        args.revision = None
        args.repo = self.repo
        args.normal = args.detailed = args.full = False
        args.repo.heads = []

        issue(args)
        self.assertIn('git sciit error fatal:',
                      sys.stdout.getvalue())
        self.assertIn('The repository has no commits.',
                      sys.stdout.getvalue())

    @patch('sciit.repo.IssueRepo.heads')
    @patch('sciit.repo.IssueRepo.sync')
    @patch('pydoc.pipepager')
    def test_command_fails_if_no_issues_matched(self, pager, sync, heads):
        args = Mock()
        args.repo = self.repo
        args.revision = self.second
        args.normal = args.detailed = args.full = False
        args.issueid = ''

        mhead = Mock()
        mhead.commit = self.second_commit
        mhead.name = 'master'
        args.repo.heads = [mhead]

        issue(args)
        self.assertIn('No issues found matching',
                      sys.stdout.getvalue())
        self.assertIn('Here are issues that are in the tracker:',
                      sys.stdout.getvalue())

    @patch('sciit.repo.IssueRepo.heads')
    @patch('sciit.repo.IssueRepo.sync')
    @patch('pydoc.pipepager')
    def test_command_returns_no_history(self, pager, sync, heads):
        args = Mock()
        args.repo = self.repo
        args.revision = self.first
        args.normal = args.detailed = args.full = False
        args.issueid = ''

        mhead = Mock()
        mhead.commit = self.second_commit
        mhead.name = 'master'
        args.repo.heads = [mhead]

        issue(args)
        self.assertIn('No issues in the repository',
                      sys.stdout.getvalue())

    @patch('sciit.repo.IssueRepo.heads')
    @patch('sciit.repo.IssueRepo.sync')
    @patch('pydoc.pipepager')
    def test_command_returns_correct_history_normal_view(self, pager, sync, heads):
        args = Mock()
        args.repo = self.repo
        args.revision = self.second
        args.normal = True
        args.detailed = args.full = False
        args.issueid = '12'

        mhead = Mock()
        mhead.commit = self.second_commit
        mhead.name = 'master'
        args.repo.heads = [mhead]

        output = issue(args)
        output = self.ansi_escape.sub('', output)
        self.assertIn('ID: 12', output)
        self.assertIn('Status: Open', output)
        self.assertIn('Description:', output)
        self.assertIn('Filepath:           path', output)
        self.assertNotIn('Issue Revisions:', output)
        self.assertNotIn('Commit Acitivity:', output)

    @patch('sciit.repo.IssueRepo.heads')
    @patch('sciit.repo.IssueRepo.sync')
    @patch('pydoc.pipepager')
    def test_command_returns_correct_history_detailed_view(self, pager, sync, heads):
        args = Mock()
        args.repo = self.repo
        args.revision = self.second
        args.detailed = True
        args.normal = args.full = False
        args.issueid = '6'

        mhead = Mock()
        mhead.commit = self.second_commit
        mhead.name = 'master'
        args.repo.heads = [mhead]

        output = issue(args)
        output = self.ansi_escape.sub('', output)
        self.assertIn('ID: 6', output)
        self.assertIn('Status: Open', output)
        self.assertIn('Description:', output)
        self.assertIn('Found In:', output)
        self.assertNotIn('Commit Acitivity:', output)

    @patch('sciit.repo.IssueRepo.heads')
    @patch('sciit.repo.IssueRepo.sync')
    @patch('pydoc.pipepager')
    def test_command_returns_correct_history_full_view(self, pager, sync, heads):
        args = Mock()
        args.repo = self.repo
        args.revision = self.second
        args.full = True
        args.normal = args.detailed = False
        args.issueid = '12'

        mhead = Mock()
        mhead.commit = self.second_commit
        mhead.name = 'master'
        args.repo.heads = [mhead]

        output = issue(args)
        output = self.ansi_escape.sub('', output)
        self.assertIn('ID: 12', output)
        self.assertIn('Status: Open', output)
        self.assertIn('Descriptions:', output)
        self.assertIn('Found In:', output)
        self.assertIn('Commit Activities:', output)
        self.assertIn('Issue Revisions:', output)
