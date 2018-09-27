import sys
from io import StringIO
from unittest import TestCase
from unittest.mock import Mock, patch

from sciit.cli.issue import issue
from tests.test_cli.external_resources import repo, second_sha, ansi_escape, second_commit, first_sha


class TestIssueCommand(TestCase):

    def setUp(self):
        self.held, sys.stdout = sys.stdout, StringIO()

    @patch('sciit.repo.IssueRepo.heads')
    @patch('sciit.repo.IssueRepo.sync')
    @patch('pydoc.pipepager')
    def test_command_fails_if_no_issues_matched(self, pager, sync, heads):
        args = Mock()
        args.repo = repo
        args.revision = second_sha
        args.normal = args.detailed = args.full = False
        args.issueid = ''

        mhead = Mock()
        mhead.commit = second_commit
        mhead.name = 'master'
        args.repo.heads = [mhead]

        issue(args)
        self.assertIn('No issues found matching',
                      sys.stdout.getvalue())
        self.assertIn('Here are issues that are in the tracker:',
                      sys.stdout.getvalue())

    @patch('sciit.repo.IssueRepo.build_history')
    @patch('sciit.repo.IssueRepo.sync')
    def test_command_returns_no_history(self, sync, history):
        args = Mock()
        args.repo = repo
        args.revision = first_sha
        args.normal = args.detailed = args.full = False
        args.issueid = ''
        history.return_value = {}

        issue(args)
        self.assertIn('No issues in the repository',
                      sys.stdout.getvalue())

    @patch('sciit.repo.IssueRepo.heads')
    @patch('sciit.repo.IssueRepo.sync')
    @patch('pydoc.pipepager')
    def test_command_returns_correct_history_normal_view(self, pager, sync, heads):
        args = Mock()
        args.repo = repo
        args.revision = second_sha
        args.normal = True
        args.detailed = args.full = False
        args.issueid = '12'

        mhead = Mock()
        mhead.commit = second_commit
        mhead.name = 'master'
        args.repo.heads = [mhead]

        output = issue(args)
        output = ansi_escape.sub('', output)
        self.assertIn('ID: 12', output)
        self.assertIn('Status: Open', output)
        self.assertIn('Description:', output)
        self.assertIn('File path:         path', output)
        self.assertNotIn('Issue Revisions:', output)
        self.assertNotIn('Commit Acitivity:', output)

    @patch('sciit.repo.IssueRepo.heads')
    @patch('sciit.repo.IssueRepo.sync')
    @patch('pydoc.pipepager')
    def test_command_returns_correct_history_detailed_view(self, pager, sync, heads):
        args = Mock()
        args.repo = repo
        args.revision = second_sha
        args.detailed = True
        args.normal = args.full = False
        args.issueid = '6'

        mhead = Mock()
        mhead.commit = second_commit
        mhead.name = 'master'
        args.repo.heads = [mhead]

        output = issue(args)
        output = ansi_escape.sub('', output)
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
        args.repo = repo
        args.revision = second_sha
        args.full = True
        args.normal = args.detailed = False
        args.issueid = '12'

        mhead = Mock()
        mhead.commit = second_commit
        mhead.name = 'master'
        args.repo.heads = [mhead]

        output = issue(args)
        output = ansi_escape.sub('', output)
        self.assertIn('ID: 12', output)
        self.assertIn('Status: Open', output)
        self.assertIn('Descriptions:', output)
        self.assertIn('Found In:', output)
        self.assertIn('Commit Activities:', output)
        self.assertIn('Issue Revisions:', output)
