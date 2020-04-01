import unittest

from unittest.mock import Mock

from git import Repo

from sciit.repo import IssueRepo
from sciit.gitlab.classes import GitRepositoryIssueClient, GitlabSciitIssueIDCache


class TestGitRepositoryIssueClient(unittest.TestCase):

    def setUp(self):

        local_git_repository_path = '../../'

        git_repository = Repo(local_git_repository_path)
        sciit_repository = IssueRepo(git_repository)

        self.git_repository_issue_client = GitRepositoryIssueClient(sciit_repository)

    def test_reset_gitlab_issues(self):

        self.gitlab_sciit_issue_id_cache = Mock()
        self.gitlab_sciit_issue_id_cache.get_sciit_issue_id = Mock(return_value='post-commit-hooks-assume-python-3')

        gitlab_issue = {
            'iid': 304,
            'title': 'Add Capability for Multiple Comments',
            'description': 'Need to add lots of comments'
        }

        self.git_repository_issue_client.handle_issue(gitlab_issue, self.gitlab_sciit_issue_id_cache)


if __name__ == '__main__':
    unittest.main()


