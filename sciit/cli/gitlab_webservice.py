# -*- coding: utf-8 -*-

from sciit.gitlab.webservice import launch_standalone
from sciit.gitlab.functions import reset_gitlab_issues, set_gitlab_api_token


def launch(args):
    launch_standalone('.')


def reset(args):
    reset_gitlab_issues(args.project_url, args.sites_local_path)


def set_token(args):
    set_gitlab_api_token(args.project_url, args.gitlab_username, args.web_hook_secret_token, args.api_token,
                         args.sites_local_path)

