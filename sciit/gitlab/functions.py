from sciit.gitlab.classes import MirroredGitlabSites
from urllib.parse import urlparse


def reset_gitlab_issues(project_url, local_git_repository_path=None):

    mirrored_gitlab_sites = MirroredGitlabSites('../')

    parsed_uri = urlparse(project_url)
    site_homepage = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    path_with_namespace = parsed_uri.path[1:]

    mirrored_gitlab_sciit_project = \
        mirrored_gitlab_sites.get_mirrored_gitlab_sciit_project(
            site_homepage, path_with_namespace, local_git_repository_path)

    mirrored_gitlab_sciit_project.reset_gitlab_issues()

