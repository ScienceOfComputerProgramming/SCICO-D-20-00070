import datetime
from unittest import TestCase
from unittest.mock import patch, Mock, MagicMock

from sciit import Issue
from sciit.web.server import app, launch

from tests.external_resources import create_mock_git_repository, create_mock_commit_with_issue_snapshots, \
    remove_existing_repo


class TestWebServerStartup(TestCase):

    def setUp(self):

        data = [{'issue_id': '1', 'title': 'the contents of the file', 'file_path': 'path',
                 'description': 'This issue had a description'},
                {'issue_id': '2', 'title': 'the contents of the file', 'file_path': 'path'},
                {'issue_id': '3', 'title': 'the contents of the file', 'file_path': 'path'},
                {'issue_id': '4', 'title': 'the contents of the file', 'file_path': 'path'},
                {'issue_id': '5', 'title': 'the contents of the file', 'file_path': 'path'},
                {'issue_id': '6',
                 'title': 'The title of your issue',
                 'description': 'A description of you issue as you\n'
                 + 'want it to be ``markdown`` supported',
                 'assignees': 'nystrome, kevin, daniels',
                 'due_date': '12 oct 2018',
                 'label': 'in-development',
                 'weight': '4',
                 'priority': 'high',
                 'file_path': 'README.md'}]

        self.commit, self.issue_snapshots = \
            create_mock_commit_with_issue_snapshots(
                '43e8d11ec2cb9802151533ae8d9c5dcc5dec91a4',
                'Nystrome',
                datetime.datetime(2018, 1, 1),
                data
            )

        self.issue = Issue('1', dict(), dict())
        self.issue.add_snapshot(self.issue_snapshots[0])

        self.mock_git_repository = create_mock_git_repository('dummy_repo', [('master', self.commit)], [self.commit])

        self.mock_issue_repository = MagicMock()
        self.mock_issue_repository.build_history.return_value = {'1': self.issue}

        self.app = app.test_client()
        self.app.testing = True

    @patch('sciit.web.server.app')
    def test_main_entrance(self, app):
        args = Mock()
        args.repo = self.mock_issue_repository
        app = self.app
        launch(args)
        pass

    @patch('sciit.web.server.global_issue_repository')
    def test_index_page(self, global_issue_repository):
        global_issue_repository._build_history.return_value = {'1': self.issue}

        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    @patch('sciit.web.server.global_issue_repository')
    def test_issue_page(self, global_issue_repository):
        global_issue_repository._build_history.return_value =\
            {'issue-1': {'status': 'Open'}, 'issue-2': {'status': 'Closed'}}

        response = self.app.get('/issue-1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        remove_existing_repo('dummy_repo')
