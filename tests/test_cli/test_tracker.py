import sys
from io import StringIO
from unittest import TestCase
from unittest.mock import Mock, patch, MagicMock

from sciit.cli.tracker import tracker

import sciit.cli.tracker

from tests.test_cli.external_resources import ansi_escape, issues, second_commit


class TestStatusCommand(TestCase):

    def setUp(self):
        self.held, sys.stdout = sys.stdout, StringIO()

        self.args = Mock()
        self.args.revision = second_commit.hexsha

        self.args.all = False
        self.args.normal = False
        self.args.detailed = False
        self.args.full = False
        self.args.open = False
        self.args.closed = False

    def test_command_finds_no_history(self):
        self.args.all = True

        self.args.repo.get_all_issues.return_value = {}

        tracker(self.args)
        self.assertIn('No issues found', sys.stdout.getvalue())

    def test_prints_correct_tracker_info(self):

        self.args.open = True

        self.args.repo.get_all_issues.return_value = {'1': issues['1']}

        output = tracker(self.args)

        output = ansi_escape.sub('', output)
        self.assertIn('ID:                1\nStatus:            Open', output)

    def test_prints_correct_tracker_info_default(self):

        self.args.repo.get_all_issues.return_value = {'2': issues['2'], '9': issues['9']}

        output = tracker(self.args)
        output = ansi_escape.sub('', output)
        self.assertIn('ID:                2\nStatus:            Open', output)
        self.assertIn('ID:                9\nStatus:            Open', output)

    @patch('tests.test_cli.external_resources.Issue.closer', new_callable=Mock(return_value='Nystrome'))
    @patch('tests.test_cli.external_resources.Issue.closed_date', new_callable=Mock(return_value='A Date'))
    @patch('sciit.cli.tracker.page', new_callable=Mock())
    def test_prints_correct_tracker_info_all(self,  closed_date, closer, page):

        self.args.all = True

        self.args.repo.get_all_issues.return_value = {
            '5': issues['5'], '4': issues['4'], 3: issues['3'], '2': issues['2'], '9': issues['9'], '6': issues['6']}

        output = tracker(self.args)
        output = ansi_escape.sub('', output)

        self.assertIn('ID:                5\nStatus:            Closed', output)
        self.assertIn('ID:                4\nStatus:            Closed', output)
        self.assertIn('ID:                3\nStatus:            Closed', output)
        self.assertIn('ID:                9\nStatus:            Open', output)
        self.assertIn('ID:                6\nStatus:            Open', output)

    @patch('tests.test_cli.external_resources.Issue.closer', new_callable=Mock(return_value='Nystrome'))
    @patch('tests.test_cli.external_resources.Issue.closed_date', new_callable=Mock(return_value='A Date'))
    def test_prints_correct_tracker_info_closed(self, closed_date, closer):

        self.args.closed = True

        self.args.repo.get_all_issues.return_value = {'5': issues['5'], '4': issues['4'], 3: issues['3']}

        output = tracker(self.args)
        output = ansi_escape.sub('', output)

        self.assertIn('ID:                5\nStatus:            Closed', output)
        self.assertIn('ID:                4\nStatus:            Closed', output)
        self.assertIn('ID:                3\nStatus:            Closed', output)
        # self.assertIn('ID:                9\nStatus:            Open', output)

    @patch('tests.test_cli.external_resources.Issue.closer', new_callable=Mock(return_value='Nystrome'))
    @patch('tests.test_cli.external_resources.Issue.closed_date', new_callable=Mock(return_value='A Date'))
    def test_prints_normal_tracker_view(self, closed_date, closer):

        self.args.all = self.args.normal = True

        self.args.repo.get_all_issues.return_value = {'5': issues['5']}

        output = tracker(self.args)
        output = ansi_escape.sub('', output)

        self.assertNotIn('Descriptions:', output)
        self.assertNotIn('File paths:', output)
        self.assertNotIn('Commit Activities:', output)
        self.assertNotIn('Found In:', output)
        self.assertNotIn('Open In Branches:', output)

    def test_prints_full_tracker_view(self):

        self.args.all = self.args.full = True

        self.args.repo.get_all_issues.return_value = {'6': issues['6']}

        output = tracker(self.args)
        output = ansi_escape.sub('', output)

        self.assertIn('Revisions to Issue (2):', output)
        self.assertIn('Present in Commits (2):', output)
