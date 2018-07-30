"""
This module tests the functionality of the cli catfile-file command.
"""
import sys
from io import StringIO
from unittest import TestCase
from unittest.mock import Mock, patch

from git import Commit
from git.util import hex_to_bin
from sciit import IssueRepo, IssueCommit, IssueTree, Issue
from sciit.cli.catfile import catfile
from tests.external_resources import safe_create_repo_dir


class TestCatFileOutput(TestCase):

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
        cls.issues = []
        for d in data:
            cls.issues.append(Issue.create(cls.repo, d))
        cls.first_issuetree = IssueTree.create(cls.repo, cls.issues)

        cls.second = '622918a4c6539f853320e06804f73d1165df69d0'
        cls.first = '43e8d11ec2cb9802151533ae8d9c5dcc5dec91a4'
        cls.second_commit = Commit(cls.repo, hex_to_bin(cls.second))
        cls.first_commit = Commit(cls.repo, hex_to_bin(cls.first))
        cls.first_issuecommit = IssueCommit.create(
            cls.repo, cls.first_commit, cls.first_issuetree)
        cls.second_issuecommit = IssueCommit.create(
            cls.repo, cls.second_commit, cls.first_issuetree)

    def setUp(self):
        self.held, sys.stdout = sys.stdout, StringIO()

    def test_command_fails_if_no_issue_repo(self):
        args = Mock()
        args.repo = IssueRepo('there')
        catfile(args)
        self.assertIn('Repository not initialized',
                      sys.stdout.getvalue())

    def test_object_cannot_be_found(self):
        args = Mock()
        args.sha = 'xxxxxsidansmd'
        args.repo = self.repo
        catfile(args)
        self.assertIn('git sciit error fatal:',
                      sys.stdout.getvalue())

    def test_get_type_issuecommit(self):
        args = Mock()
        args.type = True
        args.sha = self.first_issuecommit.hexsha
        args.repo = self.repo
        catfile(args)
        self.assertIn('issuecommit',
                      sys.stdout.getvalue())

    def test_get_type_issuetree(self):
        args = Mock()
        args.type = True
        args.sha = self.first_issuetree.hexsha
        args.repo = self.repo
        catfile(args)
        self.assertIn('issuetree',
                      sys.stdout.getvalue())

    def test_get_type_icommit(self):
        args = Mock()
        args.type = True
        args.sha = self.issues[2].hexsha
        args.repo = self.repo
        catfile(args)
        self.assertIn('issue',
                      sys.stdout.getvalue())

    def test_get_object_size(self):
        args = Mock()
        args.size = True
        args.type = False
        args.sha = self.first_issuecommit.hexsha
        args.repo = self.repo
        catfile(args)
        self.assertNotEqual('', sys.stdout.getvalue())

    @patch('pydoc.pipepager')
    def test_paged_issuecommit(self, pager):
        args = Mock()
        args.size = False
        args.type = False
        args.print = True
        args.sha = self.second_issuecommit.hexsha
        args.repo = self.repo
        output = catfile(args)
        self.assertIn('tree b7d85cba05b517db5c376c49ae14106e5b4e8972',
                      output)
        self.assertIn('issuetree 190c97e307fa9aa725bade91fb774ab8c496ebf2',
                      output)
        self.assertIn('open issues: 6',
                      output)
        self.assertIn('Initial cli framework', output)

    @patch('pydoc.pipepager')
    def test_paged_issuetree(self, pager):
        args = Mock()
        args.size = False
        args.type = False
        args.print = True
        args.sha = self.first_issuetree.hexsha
        args.repo = self.repo
        output = catfile(args)
        for issue in self.issues:
            self.assertIn(issue.hexsha,
                          output)

    @patch('pydoc.pipepager')
    def test_paged_issue(self, pager):
        args = Mock()
        args.size = False
        args.type = False
        args.print = True
        args.sha = self.issues[-1].hexsha
        args.repo = self.repo
        output = catfile(args)
        self.assertIn('Issue:         6', output)
        self.assertIn('``markdown`` supported', output)
        self.assertIn('in-development', output)
