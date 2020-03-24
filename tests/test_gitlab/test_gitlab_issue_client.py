from unittest import TestCase
from unittest.mock import Mock, MagicMock, patch

from git import Repo

from sciit.gitlab.classes import GitlabIssueClient, GitlabSciitIssueIDCache, MirroredGitlabSciitProject
from sciit import Issue, IssueRepo, IssueSnapshot


class TestGitlabIssueClient(TestCase):

    def setUp(self):

        self.gitlab_issue_client = GitlabIssueClient(
            site_homepage='https://git.dcs.gla.ac.uk',
            api_token='8b9W5ZAkDCsvJYQzhJZ2',
        )

    def test_update_issue(self):
        commit = Mock()

        data = {
            'title': 'A Test Issue',
            'description':  'Test Issue Description.',
            'issue_id': 'a-test-issue'
        }

        all_issues = dict()

        issue_snapshot = IssueSnapshot(commit, data, in_branches=['master']),
        issue = Issue('a-test-issue', all_issues, [commit])

        mock_gitlab_sciit_issue_id_cache = Mock()
        mock_gitlab_sciit_issue_id_cache.get_gitlab_issue_id=Mock(return_value=3)

        self.gitlab_issue_client.handle_issues(145, [issue], mock_gitlab_sciit_issue_id_cache)


class TestResetGitlabProjectIssues(TestCase):

    def setUp(self):

        repository_path = '../../'

        project_id = 145

        gitlab_issue_client = GitlabIssueClient(
            site_homepage='https://git.dcs.gla.ac.uk',
            api_token='8b9W5ZAkDCsvJYQzhJZ2',
        )

        git_repository = Repo(repository_path)
        local_sciit_repository = IssueRepo(git_repository)

        gitlab_sciit_issue_id_cache = GitlabSciitIssueIDCache(repository_path)

        self.mirrored_gitlab_sciit_project = MirroredGitlabSciitProject(
            project_id, gitlab_issue_client, local_sciit_repository, gitlab_sciit_issue_id_cache)

    def test_reset_gitlab_issues(self):
        self.mirrored_gitlab_sciit_project.reset_gitlab_issues()
