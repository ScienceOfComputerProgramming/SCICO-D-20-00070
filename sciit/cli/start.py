#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
# -*- coding: utf-8 -*-

import argparse
import sys

import argcomplete
import colorama

from git import Repo
from git.exc import InvalidGitRepositoryError, GitCommandError
from sciit.errors import NoCommitsError

from sciit import IssueRepo
from sciit.cli.functions import read_sciit_version, do_repository_has_no_commits_warning_and_exit, \
    do_repository_is_init_check_and_exit_if_not, do_git_command_warning_and_exit, \
    do_invalid_git_repository_warning_and_exit

from sciit.cli.close_issue import close_issue
from sciit.cli.gitlab_webservice import launch as launch_gitlab_service, reset as reset_gitlab_issues, \
    set_token as set_gitlab_api_token
from sciit.cli.init import init
from sciit.cli.issue import issue
from sciit.cli.log import log
from sciit.cli.new_issue import new_issue
from sciit.cli.status import status
from sciit.cli.tracker import tracker
from sciit.cli.web import launch as launch_web_service


def add_revision_option(parser):
    parser.add_argument(
        'revision', action='store', type=str, nargs='?',
        help=
        "the revision path to use to generate the issue log e.g. 'all' for all commits or 'master' for all commit on "
        "master branch or 'HEAD~2' from the last two commits on current branch. See git rev-list options for more "
        "path options")


def add_new_issue_options(parser):
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-p', '--push', help='pushes the newly created issue branch to the origin', action='store_true')
    group.add_argument(
        '-a', '--accept', help='accepts the newly created issue branch by merging it to master locally',
        action='store_true')


def add_issue_filter_options(parser):
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-a', '--all', help='show all the issues currently tracked and their status', action='store_true')
    group.add_argument(
        '-o', '--open', help='default: show only issues that are open', action='store_true')
    group.add_argument('-c', '--closed', help='show only issues that are closed', action='store_true')


def add_view_options(parser):
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-f', '--full', action='store_true',
        help=
        'view the full  information for issues including, description, commit activity, multiple file paths, open in, '
        'and found in branches')
    group.add_argument(
        '-n', '--normal', action='store_true',
        help='default: view summary issue information')


def add_gitlab_reset_parser(gitlab_subparsers):
    gitlab_reset_parser = gitlab_subparsers.add_parser(
        'reset', description='resets all issues in the Gitlab database')
    gitlab_reset_parser.set_defaults(func=reset_gitlab_issues)

    gitlab_reset_parser.add_argument('project_url')
    gitlab_reset_parser.add_argument('sites_local_path')


def add_gitlab_set_credentials_parser(gitlab_subparsers):
    gitlab_set_token_parser = gitlab_subparsers.add_parser(
        'set_credentials', description=
        'sets a Gitlab username, web hook token and API token for a Gitlab project to be used by the sciit gitlab '
        'service')
    gitlab_set_token_parser.set_defaults(func=set_gitlab_api_token)
    gitlab_set_token_parser.add_argument('project_url')
    gitlab_set_token_parser.add_argument('gitlab_username')
    gitlab_set_token_parser.add_argument('web_hook_secret_token')
    gitlab_set_token_parser.add_argument('api_token')
    gitlab_set_token_parser.add_argument('sites_local_path')


def add_gitlab_parser(subparsers):

    gitlab_parser = subparsers.add_parser('gitlab')
    gitlab_subparsers = gitlab_parser.add_subparsers()

    gitlab_start_parser = gitlab_subparsers.add_parser(
        'start', description='launches the gitlab webservice that integrates gitlab issues with sciit')
    gitlab_start_parser.set_defaults(func=launch_gitlab_service)

    add_gitlab_reset_parser(gitlab_subparsers)
    add_gitlab_set_credentials_parser(gitlab_subparsers)


def create_command_parser(issue_repository):

    parser = argparse.ArgumentParser(
        prog='git sciit',
        description=
        'To use the application you can create your issues anywhere in your source code as block comments in a '
        'particular format and it will become a versioned object within your git environment. Operations '
        'done with git will run git sciit in the background in order to automate issue tracking for you. '
    )
    parser.add_argument('-v', '--version', action='version', version=read_sciit_version())

    subparsers = parser.add_subparsers()

    init_parser = subparsers.add_parser(
        name='init',
        description=
        'create an empty issue repository or build an issue repository from source code comments in past commits'
    )
    init_parser.set_defaults(func=init)
    init_parser.add_argument(
        '-r', '--reset', action='store_true', help='resets the issue repo and rebuild from past commits')
    init_parser.add_argument(
        '-s', '--synchronize', action='store_true', help='synchronizes repository with remotes before initialisation')

    status_parser = subparsers.add_parser(
        name='status',
        description=
        'shows the user how many issues are open and how many are closed on all branches'
    )
    status_parser.set_defaults(func=status)
    add_revision_option(status_parser)
    add_view_options(status_parser)

    log_parser = subparsers.add_parser(
        'log', description='shows a log that is similar to the git log but shows open issues')
    log_parser.set_defaults(func=log)

    add_revision_option(log_parser)

    tracker_parser = subparsers.add_parser('tracker', description='prints a log that shows issues and their status')
    tracker_parser.set_defaults(func=tracker)
    add_revision_option(tracker_parser)

    add_issue_filter_options(tracker_parser)
    add_view_options(tracker_parser)

    issue_parser = subparsers.add_parser('issue', description='shows information about the issue with the given id')
    issue_parser.set_defaults(func=issue)

    add_view_options(issue_parser)

    def issue_id_completer(**kwargs):
        return issue_repository.issue_keys()

    issue_parser.add_argument(
        'issue_id', action='store', type=str,
        help='The id of the issue to display').completer = issue_id_completer

    add_revision_option(issue_parser)

    web_parser = subparsers.add_parser(
        'web',
        description='launches a local web interface for the sciit issue tracker')
    web_parser.set_defaults(func=launch_web_service)

    add_gitlab_parser(subparsers)

    new_parser = subparsers.add_parser(
        'new',
        description='creates a new issue in the project backlog on a branch specified by the issue id')
    new_parser.set_defaults(func=new_issue)

    add_new_issue_options(new_parser)

    close_parser = subparsers.add_parser(
        'close',
        description='closes an issue in the current branch')
    close_parser.set_defaults(func=close_issue)

    close_parser.add_argument(
        'issue_id', action='store', type=str,
        help='the id of the issue to be closed')

    return parser


def main():
    colorama.init()

    git_repository = None
    try:
        git_repository = Repo(search_parent_directories=True)
    except InvalidGitRepositoryError:
        pass

    try:
        issue_repository = None
        if git_repository is not None:
            issue_repository = IssueRepo(git_repository)
            issue_repository.cli = True

        parser = create_command_parser(issue_repository)
        argcomplete.autocomplete(parser)
        args = parser.parse_args()

        if not hasattr(args, 'func'):
            parser.print_help()
        elif args.func in {set_gitlab_api_token, reset_gitlab_issues}:
             args.func(args)
        elif git_repository is None:
            do_invalid_git_repository_warning_and_exit()
        else:
            args.repo = issue_repository
            if args.func == init:
                args.func(args)
            else:
                do_repository_is_init_check_and_exit_if_not(issue_repository)
                args.func(args)

    except NoCommitsError:
        do_repository_has_no_commits_warning_and_exit()
    except GitCommandError as gce:
        do_git_command_warning_and_exit(gce.command)

    # Forces proper clean up of git repository resources on Windows.
    # See https://github.com/gitpython-developers/GitPython/issues/508
    if git_repository is not None:
        git_repository.__del__()


def start():
    if __name__ == '__main__':
        sys.exit(main())


start()
