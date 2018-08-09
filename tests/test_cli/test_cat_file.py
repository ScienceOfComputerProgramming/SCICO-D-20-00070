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
from tests.test_cli.external_resources import repo, first_icommit, first_itree, first_issues, second_icommit


class TestCatFileCommand(TestCase):

    def setUp(self):
        self.held, sys.stdout = sys.stdout, StringIO()

    def test_object_cannot_be_found(self):
        args = Mock()
        args.sha = 'xxxxxsidansmd'
        args.repo = repo
        catfile(args)
        self.assertIn('git sciit error fatal:',
                      sys.stdout.getvalue())

    def test_get_type_issuecommit(self):
        args = Mock()
        args.type = True
        args.sha = first_icommit.hexsha
        args.repo = repo
        catfile(args)
        self.assertIn('issuecommit',
                      sys.stdout.getvalue())

    def test_get_type_issuetree(self):
        args = Mock()
        args.type = True
        args.sha = first_itree.hexsha
        args.repo = repo
        catfile(args)
        self.assertIn('issuetree',
                      sys.stdout.getvalue())

    def test_get_type_icommit(self):
        args = Mock()
        args.type = True
        args.sha = first_issues[2].hexsha
        args.repo = repo
        catfile(args)
        self.assertIn('issue',
                      sys.stdout.getvalue())

    def test_get_object_size(self):
        args = Mock()
        args.size = True
        args.type = False
        args.sha = first_icommit.hexsha
        args.repo = repo
        catfile(args)
        self.assertNotEqual('', sys.stdout.getvalue())

    @patch('pydoc.pipepager')
    def test_paged_issuecommit(self, pager):
        args = Mock()
        args.size = False
        args.type = False
        args.print = True
        args.sha = second_icommit.hexsha
        args.repo = repo
        output = catfile(args)
        self.assertIn('tree b7d85cba05b517db5c376c49ae14106e5b4e8972',
                      output)
        self.assertIn('issuetree dc214cf96764bd7b7e820ce2c232d53f5f074914',
                      output)
        self.assertIn('open issues: 5',
                      output)
        self.assertIn('Initial cli framework', output)

    @patch('pydoc.pipepager')
    def test_paged_issuetree(self, pager):
        args = Mock()
        args.size = False
        args.type = False
        args.print = True
        args.sha = first_itree.hexsha
        args.repo = repo
        output = catfile(args)
        for issue in first_issues:
            self.assertIn(issue.hexsha,
                          output)

    @patch('pydoc.pipepager')
    def test_paged_issue(self, pager):
        args = Mock()
        args.size = False
        args.type = False
        args.print = True
        args.sha = first_issues[-1].hexsha
        args.repo = repo
        output = catfile(args)
        self.assertIn('Issue:         6', output)
        self.assertIn('``markdown`` supported', output)
        self.assertIn('in-development', output)
