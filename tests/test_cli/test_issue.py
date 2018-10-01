import sys
from io import StringIO
from unittest import TestCase
from unittest.mock import Mock, patch

from sciit.cli.issue import issue
from tests.test_cli.external_resources import ansi_escape, first_sha, repo, second_sha, second_commit


class TestIssueCommand(TestCase):

    def setUp(self):
        self.held, sys.stdout = sys.stdout, StringIO()
        self.args = Mock()
        self.args.repo = repo

    @patch('sciit.repo.IssueRepo.heads')
    @patch('sciit.repo.IssueRepo.sync')
    @patch('pydoc.pipepager')
    def test_command_fails_if_no_issues_matched(self, pager, sync, heads):
        self.args.revision = second_sha
        self.args.normal = self.args.detailed = self.args.full = False
        self.args.issueid = ''

        mock_head = Mock()
        mock_head.commit = second_commit
        mock_head.name = 'master'
        self.args.repo.heads = [mock_head]

        issue(self.args)
        self.assertIn('No issues found matching', sys.stdout.getvalue())
        self.assertIn('Here are issues that are in the tracker:', sys.stdout.getvalue())

    @patch('sciit.repo.IssueRepo.build_history')
    @patch('sciit.repo.IssueRepo.sync')
    def test_command_returns_no_history(self, sync, history):
        self.args.revision = first_sha
        self.args.normal = self.args.detailed = self.args.full = False
        self.args.issueid = ''
        history.return_value = {}

        issue(self.args)
        self.assertIn('No issues in the repository',
                      sys.stdout.getvalue())

    @patch('sciit.repo.IssueRepo.heads')
    @patch('sciit.repo.IssueRepo.sync')
    @patch('pydoc.pipepager')
    def test_command_returns_correct_history_normal_view(self, pager, sync, heads):
        self.args.revision = second_sha
        self.args.normal = True
        self.args.detailed = self.args.full = False
        self.args.issueid = '12'

        mock_head = Mock()
        mock_head.commit = second_commit
        mock_head.name = 'master'
        self.args.repo.heads = [mock_head]

        output = issue(self.args)
        output = ansi_escape.sub('', output)
        self.assertIn('ID:                12', output)
        self.assertIn('Status:            Open', output)
        self.assertIn('Description:', output)
        self.assertIn('Latest file path:  path', output)
        self.assertNotIn('IssueSnapshot Revisions:', output)
        self.assertNotIn('Commit Activity:', output)

    @patch('sciit.repo.IssueRepo.heads')
    @patch('sciit.repo.IssueRepo.sync')
    @patch('pydoc.pipepager')
    def test_command_returns_correct_history_detailed_view(self, pager, sync, heads):
        self.args.revision = second_sha
        self.args.detailed = True
        self.args.normal = self.args.full = False
        self.args.issueid = '6'

        mock_head = Mock()
        mock_head.commit = second_commit
        mock_head.name = 'master'
        self.args.repo.heads = [mock_head]

        output = issue(self.args)
        output = ansi_escape.sub('', output)
        self.assertIn('ID:                6', output)
        self.assertIn('Status:            Open', output)
        self.assertIn('Existed in:', output)
        self.assertNotIn('Commit Activity:', output)

    @patch('sciit.repo.IssueRepo.heads')
    @patch('sciit.repo.IssueRepo.sync')
    @patch('pydoc.pipepager')
    def test_command_returns_correct_history_full_view(self, pager, sync, heads):
        self.args.revision = second_sha
        self.args.full = True
        self.args.normal = self.args.detailed = False
        self.args.issueid = '12'

        mock_head = Mock()
        mock_head.commit = second_commit
        mock_head.name = 'master'
        self.args.repo.heads = [mock_head]

        output = issue(self.args)
        output = ansi_escape.sub('', output)
        self.assertIn('ID:                12', output)
        self.assertIn('Status:            Open', output)
        self.assertIn('Existed in:', output)
        self.assertIn('Present in Commits (1):', output)
        self.assertIn('Revisions to Issue (1):', output)
