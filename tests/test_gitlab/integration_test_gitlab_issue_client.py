from unittest import TestCase
from unittest.mock import Mock

from sciit.gitlab.classes import GitlabIssueClient, GitlabTokenCache
from sciit import Issue, IssueSnapshot


class TestGitlabIssueClient(TestCase):

    def setUp(self):

        self.path_with_namespace = 'twsswt/sciit-gitlab-test'

        gitlab_token_cache = GitlabTokenCache('../../../')
        api_token = gitlab_token_cache.get_api_token(self.path_with_namespace)

        self.gitlab_issue_client = GitlabIssueClient(
            site_homepage='https://git.dcs.gla.ac.uk',
            api_token=api_token,
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
        issue.add_snapshot(issue_snapshot)

        mock_gitlab_sciit_issue_id_cache = Mock()
        mock_gitlab_sciit_issue_id_cache.get_gitlab_issue_id=Mock(return_value=3)

        self.gitlab_issue_client.handle_issues(self.path_with_namespace, [issue], mock_gitlab_sciit_issue_id_cache)


