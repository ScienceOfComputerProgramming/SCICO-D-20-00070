import unittest

from git import Repo

from sciit.repo import IssueRepo
from sciit.gitlab.classes import GitRepositoryIssueClient, GitlabSciitIssueIDCache


class TestGitRepositoryIssueClient(unittest.TestCase):

    def setUp(self):

        local_git_repository_path = '../../'

        git_repository = Repo(local_git_repository_path)
        sciit_repository = IssueRepo(git_repository)

        self.git_repository_issue_client = GitRepositoryIssueClient(sciit_repository)
        self.gitlab_sciit_issue_id_cache = GitlabSciitIssueIDCache(local_git_repository_path)

    def test_reset_gitlab_issues(self):

        gitlab_issue = {'iid': 248} # 'update-manual-for-new-command'

        self.git_repository_issue_client.handle_issue(gitlab_issue, self.gitlab_sciit_issue_id_cache)


if __name__ == '__main__':
    unittest.main()


