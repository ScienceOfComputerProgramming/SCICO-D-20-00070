import sys
from io import StringIO
from unittest import TestCase
from unittest.mock import Mock, patch

from sciit.cli.cat_file import cat_file
from tests.test_cli.external_resources import repo, first_issue_commit, first_issue_tree, first_issues, \
    second_issue_commit


class TestCatFileCommand(TestCase):

    def setUp(self):
        self.held, sys.stdout = sys.stdout, StringIO()

    def test_object_cannot_be_found(self):
        args = Mock()
        args.sha = 'xxxxxsidansmd'
        args.repo = repo
        cat_file(args)
        self.assertIn('git sciit error fatal:',
                      sys.stdout.getvalue())

    def test_get_type_issuecommit(self):
        args = Mock()
        args.type = True
        args.sha = first_issue_commit.hexsha
        args.repo = repo
        cat_file(args)
        self.assertIn('IssueCommit', sys.stdout.getvalue())

    def test_get_type_issuetree(self):
        args = Mock()
        args.type = True
        args.sha = first_issue_tree.hexsha
        args.repo = repo
        cat_file(args)
        self.assertIn('IssueTree', sys.stdout.getvalue())

    def test_get_type_icommit(self):
        args = Mock()
        args.type = True
        args.sha = first_issues[2].hexsha
        args.repo = repo
        cat_file(args)
        self.assertIn('Issue', sys.stdout.getvalue())

    def test_get_object_size(self):
        args = Mock()
        args.size = True
        args.type = False
        args.sha = first_issue_commit.hexsha
        args.repo = repo
        cat_file(args)
        self.assertNotEqual('', sys.stdout.getvalue())

    @patch('pydoc.pipepager')
    def test_paged_issuecommit(self, pager):
        args = Mock()
        args.size = False
        args.type = False
        args.print = True
        args.sha = second_issue_commit.hexsha
        args.repo = repo
        output = cat_file(args)
        self.assertIn('tree b7d85cba05b517db5c376c49ae14106e5b4e8972', output)
        self.assertIn('issuetree dc214cf96764bd7b7e820ce2c232d53f5f074914', output)
        self.assertIn('open issues: 5',  output)
        self.assertIn('Initial cli framework', output)

    @patch('pydoc.pipepager')
    def test_paged_issuetree(self, pager):
        args = Mock()
        args.size = False
        args.type = False
        args.print = True
        args.sha = first_issue_tree.hexsha
        args.repo = repo
        output = cat_file(args)
        for issue in first_issues:
            self.assertIn(issue.hexsha, output)

    @patch('pydoc.pipepager')
    def test_paged_issue(self, pager):
        args = Mock()
        args.size = False
        args.type = False
        args.print = True
        args.sha = first_issues[-1].hexsha
        args.repo = repo
        output = cat_file(args)
        self.assertIn('Issue:         6', output)
        self.assertIn('``markdown`` supported', output)
        self.assertIn('in-development', output)
