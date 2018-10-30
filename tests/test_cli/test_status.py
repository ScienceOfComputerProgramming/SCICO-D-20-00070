import sys
from io import StringIO
from unittest import TestCase
from unittest.mock import Mock, patch

from sciit.cli.status import status
from tests.test_cli.external_resources import second_commit, issues


class TestStatusCommand(TestCase):

    def setUp(self):
        self.held, sys.stdout = sys.stdout, StringIO()
        self.args = Mock()
        self.args.repo.head = second_commit.second_sha
        mock_head = Mock()
        mock_head.commit = second_commit
        mock_head.name = 'master'
        self.args.repo.heads = [mock_head]

    @patch('sciit.cli.functions.page', new_callable=Mock)
    def test_prints_correct_status_info(self, page):
        self.args.revision = False
        self.args.repo.get_all_issues.return_value = {str(i): issues[str(i)] for i in [1, 2, 3, 4, 5, 6, 9, 12]}

        status(self.args)

        self.assertIn('Open Issues:   5', page.call_args[0][0])
        self.assertIn('Closed Issues: 3', page.call_args[0][0])

    @patch('sciit.cli.functions.page', new_callable=Mock)
    def test_prints_correct_status_info_with_revision(self, page):
        self.args.repo.get_all_issues.return_value = {str(i): issues[str(i)] for i in [1, 2, 3, 4, 5, 6, 9, 12]}

        status(self.args)
        self.assertIn('Open Issues:   5', page.call_args[0][0])
        self.assertIn('Closed Issues: 3', page.call_args[0][0])
