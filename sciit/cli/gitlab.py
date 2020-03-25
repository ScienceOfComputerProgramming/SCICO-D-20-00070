from sciit.gitlab.webservice import launch as launch_web_service
from sciit.gitlab.functions import reset_gitlab_issues


def launch(args):
    launch_web_service('.')


def reset(args):
    reset_gitlab_issues(args.project_url)
