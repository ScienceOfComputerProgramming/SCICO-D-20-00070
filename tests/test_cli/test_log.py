"""
This module tests the functionality of the cli log command.
"""
import sys
from io import StringIO
from unittest import TestCase
from unittest.mock import Mock, patch

from git import Commit
from git.util import hex_to_bin
from sciit import IssueRepo, IssueCommit, IssueTree, Issue
from sciit.cli.log import log
from sciit.functions import write_last_issue
from tests.external_resources import safe_create_repo_dir


class TestLogCommand(TestCase):

    @classmethod
    def setUpClass(cls):
        safe_create_repo_dir('here')
        cls.repo = IssueRepo('here')

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
        log(args)
        self.assertIn('Repository not initialized',
                      sys.stdout.getvalue())

    @patch('sciit.repo.IssueRepo.sync')
    def test_command_fails_if_bad_revision(self, sync):
        args = Mock()
        args.repo = self.repo
        args.revision = 'asdfesdasd'
        log(args)
        self.assertIn('git sciit error fatal: bad revision ',
                      sys.stdout.getvalue())

    @patch('sciit.repo.IssueRepo.head')
    @patch('sciit.repo.IssueRepo.sync')
    @patch('pydoc.pipepager')
    def test_log_generates_correctly_from_two_commits(self, pager, sync, head):
        args = Mock()
        args.revision = False
        args.repo = self.repo
        args.repo.head = self.second
        output = log(args)
        self.assertIn('commit ' + self.second, output)
        self.assertIn('Open Issues: 5', output)
        self.assertIn('commit ' + self.first, output)
        self.assertIn('Open Issues: 6', output)
