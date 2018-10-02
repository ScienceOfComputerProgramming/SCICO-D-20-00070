from unittest import TestCase
from unittest.mock import patch, Mock

from git import Commit
from git.util import hex_to_bin

from sciit import IssueRepo, IssueListInCommit, IssueSnapshot
from sciit.web.server import app, launch

from tests.external_resources import safe_create_repo_dir


class TestWebServerStartup(TestCase):

    def setUp(self):
        safe_create_repo_dir('here')
        self.repo = IssueRepo('here')

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

        self.issues = [IssueSnapshot.create_from_data(self.repo, d) for d in data]

        self.first = '43e8d11ec2cb9802151533ae8d9c5dcc5dec91a4'
        self.first_commit = Commit(self.repo, hex_to_bin(self.first))
        self.first_issue_commit = \
            IssueListInCommit.create_from_commit_and_issues(self.repo, self.first_commit, self.issues)

        self.app = app.test_client()
        self.app.testing = True

    @patch('sciit.repo.IssueRepo.iter_issue_commits')
    @patch('sciit.repo.IssueRepo.heads')
    @patch('sciit.web.server.app')
    def test_main_entrance(self, app, heads, issue_commits):
        args = Mock()
        args.repo = self.repo
        app = self.app
        mock_head = Mock()
        mock_head.commit.hexsha = self.first
        mock_head.name = 'master'
        args.repo.heads = [mock_head]
        issue_commits.return_value = [self.first_issue_commit]
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
