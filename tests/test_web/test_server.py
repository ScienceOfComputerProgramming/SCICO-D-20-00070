import datetime
from unittest import TestCase
from unittest.mock import patch, Mock, MagicMock

from sciit import IssueRepo, Issue
from sciit.web.server import app, launch

from tests.external_resources import create_mock_git_repository, create_mock_commit_with_issue_snapshots


class TestWebServerStartup(TestCase):

    def setUp(self):

        data = [{'issue_id': '1', 'title': 'the contents of the file', 'filepath': 'path',
                 'description': 'This issue had a description'},
                {'issue_id': '2', 'title': 'the contents of the file', 'filepath': 'path'},
                {'issue_id': '3', 'title': 'the contents of the file', 'filepath': 'path'},
                {'issue_id': '4', 'title': 'the contents of the file', 'filepath': 'path'},
                {'issue_id': '5', 'title': 'the contents of the file', 'filepath': 'path'},
                {'issue_id': '6',
                 'title': 'The title of your issue',
                 'description': 'A description of you issue as you\n'
                 + 'want it to be ``markdown`` supported',
                 'assignees': 'nystrome, kevin, daniels',
                 'due_date': '12 oct 2018',
                 'label': 'in-development',
                 'weight': '4',
                 'priority': 'high',
                 'filepath': 'README.md'}]

        self.commit, self.issue_snapshots = \
            create_mock_commit_with_issue_snapshots(
                '43e8d11ec2cb9802151533ae8d9c5dcc5dec91a4',
                'Nystrome',
                datetime.datetime(2018, 1, 1),
                data
            )

        issue = Issue('1', dict())
        issue.update(self.issue_snapshots[0])

        self.mock_git_repository = create_mock_git_repository('here', [('master', self.commit)], [self.commit])

        self.mock_issue_repository = MagicMock()
        self.mock_issue_repository.build_history.return_value = {'1': issue}

        self.app = app.test_client()
        self.app.testing = True

    @patch('sciit.web.server.app')
    def test_main_entrance(self, app):
        args = Mock()
        args.repo = self.mock_issue_repository
        app = self.app
        launch(args)
        pass

    @patch('sciit.web.server.history')
    def test_index_page(self, history):
        history = {'issue-1': {'status': 'Open'}, 'issue-2': {'status': 'Closed'}}

        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    @patch('sciit.web.server.history')
    def test_issue_page(self, history):
        history = {'issue-1': {'status': 'Open'}, 'issue-2': {'status': 'Closed'}}

        response = self.app.get('/issue-1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
