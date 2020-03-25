from sciit.gitlab.webservice import launch as launch_web_service
from sciit.gitlab.functions import reset_gitlab_issues, set_gitlab_api_token


def launch(args):
    launch_web_service('.')


def reset(args):
    reset_gitlab_issues(args.project_url, args.local_git_repository_path)


def set_token(args):
    set_gitlab_api_token(args.project_url, args.api_token)

