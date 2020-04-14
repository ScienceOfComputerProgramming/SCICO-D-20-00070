from sciit.gitlab.classes import MirroredGitlabSites
from urllib.parse import urlparse


def reset_gitlab_issues(project_url, sites_local_path):

    mirrored_gitlab_sites = MirroredGitlabSites(sites_local_path)

    parsed_uri = urlparse(project_url)
    site_homepage = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
    path_with_namespace = parsed_uri.path

    mirrored_gitlab_sciit_project = \
        mirrored_gitlab_sites.get_mirrored_gitlab_sciit_project(
            site_homepage, path_with_namespace)

    mirrored_gitlab_sciit_project.reset_gitlab_issues()


def set_gitlab_api_token(project_url, gitlab_username, web_hook_secret_token, api_token, sites_local_path):
    mirrored_gitlab_sites = MirroredGitlabSites(sites_local_path)

    parsed_uri = urlparse(project_url)
    site_homepage = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
    path_with_namespace = parsed_uri.path

    mirrored_gitlab_site = mirrored_gitlab_sites.get_mirrored_gitlab_site(site_homepage)
    mirrored_gitlab_site.set_credentials(path_with_namespace, gitlab_username, web_hook_secret_token, api_token)
