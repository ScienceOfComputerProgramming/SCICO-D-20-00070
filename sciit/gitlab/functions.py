from git import Repo

from sciit.gitlab.classes import GitlabIssueClient, GitlabSciitIssueIDCache, MirroredGitlabSciitProject
from sciit import IssueRepo


def reset_gitlab_issues(site_homepage, api_token, project_id):

    repository_path = './'

    gitlab_issue_client = GitlabIssueClient(site_homepage, api_token)

    git_repository = Repo(repository_path)
    local_sciit_repository = IssueRepo(git_repository)

    gitlab_sciit_issue_id_cache = GitlabSciitIssueIDCache(repository_path)

    mirrored_gitlab_sciit_project = MirroredGitlabSciitProject(
        project_id, gitlab_issue_client, local_sciit_repository, gitlab_sciit_issue_id_cache)

    mirrored_gitlab_sciit_project.reset_gitlab_issues()
