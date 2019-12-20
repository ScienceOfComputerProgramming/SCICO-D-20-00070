from unittest import TestCase
from unittest.mock import Mock, MagicMock, patch

from git import Repo

from sciit.gitlab.classes import GitlabIssueClient, GitlabSciitIssueIDCache
from sciit import IssueSnapshot, IssueRepo


class TestGitlabIssueClient(TestCase):

    def setUp(self):

        self.gitlab_issue_client = GitlabIssueClient(
            site_homepage='https://git.dcs.gla.ac.uk',
            api_token='8b9W5ZAkDCsvJYQzhJZ2',
        )

    def test_update_issue(self):
        commit = Mock()

        data = {
            'title': 'A Test Issue XZEssZXZ',
            'description':  'Test Issue Description XXXXPWS.',
            'issue_id': 'a-test-issue'
        }

        issue_snapshots = [
            IssueSnapshot(commit, data, in_branches=['master']),
        ]

        mock_gitlab_sciit_issue_id_cache = Mock()
        mock_gitlab_sciit_issue_id_cache.get_gitlab_issue_id=Mock(return_value=3)

        self.gitlab_issue_client.handle_issue_snapshots(145, issue_snapshots, mock_gitlab_sciit_issue_id_cache)


class TestResetGitlabProjectIssues(TestCase):

    def setUp(self):

        self.gitlab_issue_client = GitlabIssueClient(
            site_homepage='https://git.dcs.gla.ac.uk',
            api_token='8b9W5ZAkDCsvJYQzhJZ2',
        )

        git_repository = Repo('../../')
        self.local_sciit_repository = IssueRepo(git_repository)

        self.gitlab_sciit_issue_id_cache = GitlabSciitIssueIDCache('../../')

    def test_reset_gitlab_issues(self):
        self.gitlab_issue_client.clear_gitlab_issues(145)
        issue_snapshots = self.local_sciit_repository.find_issue_snapshots()
        self.gitlab_issue_client.handle_issue_snapshots(145, issue_snapshots, self.gitlab_sciit_issue_id_cache)
