from sciit.gitlab.webservice import launch as launch_web_service
from sciit.gitlab.functions import reset_gitlab_issues


def launch(args):
    launch_web_service('.')


def reset(args):
    site_homepage, api_token, project_id

    reset_gitlab_issues()
