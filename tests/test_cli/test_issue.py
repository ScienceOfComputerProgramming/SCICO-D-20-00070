import sys
from io import StringIO
from unittest import TestCase
from unittest.mock import Mock, patch, MagicMock

from sciit.cli.issue import issue
from tests.test_cli.external_resources import ansi_escape, first_commit, second_commit, issues


class TestIssueCommand(TestCase):

    def setUp(self):
        self.held, sys.stdout = sys.stdout, StringIO()
        self.args = Mock()
        self.args.repo = MagicMock()

    def test_command_fails_if_no_issues_matched(self):
        self.args.repo.get_issue=Mock(return_value=None)
        self.args.repo.get_issue_keys=Mock(return_value=['1]'])
        issue(self.args)

        self.assertIn('No issues found matching', sys.stdout.getvalue())
        self.assertIn('Here are issues that are in the tracker:', sys.stdout.getvalue())

    def test_command_returns_no_history(self):
        self.args.revision = first_commit.hexsha
        self.args.normal = self.args.detailed = self.args.full = False
        self.args.issue_id = ''

        self.args.repo.get_issue = Mock(return_value=None)

        issue(self.args)
        self.assertIn('No issues in the repository', sys.stdout.getvalue())

    @patch('tests.external_resources.IssueSnapshot.in_branches', new_callable=MagicMock(return_value=['master']))
    @patch('sciit.cli.issue.page', new_callable=Mock())
    def test_command_returns_correct_history_normal_view(self, in_branches, _):

        self.args.revision = second_commit.hexsha
        self.args.normal = True
        self.args.detailed = self.args.full = False
        self.args.issue_id = '12'
        self.args.repo.get_issue.return_value = issues['12']

        output = issue(self.args)
        output = ansi_escape.sub('', output)

        self.assertIn('ID:                12', output)
        self.assertIn('Status:            Open', output)
        self.assertIn('Description:', output)
        self.assertIn('Latest file path:  path', output)
        self.assertNotIn('IssueSnapshot Revisions:', output)
        self.assertNotIn('Commit Activity:', output)

    @patch('sciit.cli.issue.page', new_callable=Mock())
    def test_command_returns_correct_history_full_view(self, _):
        self.args.revision = second_commit.hexsha
        self.args.full = True
        self.args.normal = self.args.detailed = False
        self.args.issue_id = '12'
        self.args.repo.get_issue.return_value = issues['12']

        output = issue(self.args)

        output = ansi_escape.sub('', output)
        self.assertIn('ID:                12', output)
        self.assertIn('Status:            Open', output)
        self.assertIn('Branch file paths:', output)
        self.assertIn('Present in Commits (1):', output)
        self.assertIn('Revisions to Issue (1):', output)
