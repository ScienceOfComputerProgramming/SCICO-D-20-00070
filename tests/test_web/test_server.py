"""
This module tests the functionality of the cli tracker command.
"""
from unittest import TestCase
from unittest.mock import patch, PropertyMock, Mock

from git import Commit
from git.util import hex_to_bin

from sciit import IssueRepo, IssueCommit, IssueTree, Issue
from sciit.web.server import app, launch

from tests.external_resources import safe_create_repo_dir


class TestWebServerStartup(TestCase):

    @classmethod
    def setUpClass(cls):
        safe_create_repo_dir('here')
        cls.repo = IssueRepo('here')

        data = [{'id': '1', 'title': 'the contents of the file', 'filepath': 'path',
                 'description': 'This issue had a description'},
                {'id': '2', 'title': 'the contents of the file', 'filepath': 'path'},
                {'id': '3', 'title': 'the contents of the file', 'filepath': 'path'},
                {'id': '4', 'title': 'the contents of the file', 'filepath': 'path'},
                {'id': '5', 'title': 'the contents of the file', 'filepath': 'path'},
                {'id': '6',
                 'title': 'The title of your issue',
                 'description': 'A description of you issue as you\n'
                 + 'want it to be ``markdown`` supported',
                 'assignees': 'nystrome, kevin, daniels',
                 'due_date': '12 oct 2018',
                 'label': 'in-development',
                 'weight': '4',
                 'priority': 'high',
                 'filepath': 'README.md'}]

        cls.issues = []
        for d in data:
            cls.issues.append(Issue.create_from_data(cls.repo, d))
        cls.itree = IssueTree.create(cls.repo, cls.issues)

        cls.first = '43e8d11ec2cb9802151533ae8d9c5dcc5dec91a4'
        cls.first_commit = Commit(cls.repo, hex_to_bin(cls.first))
        cls.first_icommit = IssueCommit.create(cls.repo, cls.first_commit, cls.itree)

        cls.app = app.test_client()
        cls.app.testing = True

    @patch('sciit.repo.IssueRepo.iter_issue_commits')
    @patch('sciit.repo.IssueRepo.heads')
    @patch('sciit.web.server.app')
    def test_main_entrance(self, app, heads, icommits):
        args = Mock()
        args.repo = self.repo
        app = self.app
        mock_head = Mock()
        mock_head.commit.hexsha = self.first
        mock_head.name = 'master'
        args.repo.heads = [mock_head]
        icommits.return_value = [self.first_icommit]
        launch(args)
        pass

    @patch('sciit.web.server.history')
    def test_index_page(self, history):
        history = {'issue-1': {'status': 'Open'},
                   'issue-2': {'status': 'Closed'}}
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    @patch('sciit.web.server.history')
    def test_issue_page(self, history):
        history = {'issue-1': {'status': 'Open'},
                   'issue-2': {'status': 'Closed'}}
        response = self.app.get('/issue-1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
