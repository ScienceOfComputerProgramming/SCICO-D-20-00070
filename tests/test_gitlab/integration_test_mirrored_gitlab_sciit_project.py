import unittest

from git import Repo

from sciit.gitlab.classes import GitlabIssueClient, GitlabSciitIssueIDCache, GitlabTokenCache,\
    MirroredGitlabSciitProject
from sciit import IssueRepo


class TestMirroredGitlabSciitProject(unittest.TestCase):

    def setUp(self):
        repository_path = '../../'

        project_id = 145

        gitlab_token_cache = GitlabTokenCache('../../../')
        api_token = gitlab_token_cache.get_gitlab_api_token(project_id)

        gitlab_issue_client = GitlabIssueClient(
            site_homepage='https://git.dcs.gla.ac.uk',
            api_token=api_token,
        )

        git_repository = Repo(repository_path)
        local_sciit_repository = IssueRepo(git_repository)

        gitlab_sciit_issue_id_cache = GitlabSciitIssueIDCache(repository_path)


        self.mirrored_gitlab_sciit_project = MirroredGitlabSciitProject(
            project_id, gitlab_issue_client, local_sciit_repository, gitlab_sciit_issue_id_cache)

    def test_reset_gitlab_issues(self):
        self.mirrored_gitlab_sciit_project.reset_gitlab_issues()


if __name__ == '__main__':
    unittest.main()
