# -*- coding: utf-8 -*-
"""
main() entry point of the command line interface that accepts the command line arguments and pass them to the
appropriate module for handling.
"""

import argparse
import sys
import colorama

from git import Repo
from git.exc import InvalidGitRepositoryError, GitCommandError
from sciit.errors import RepoObjectDoesNotExistError, NoCommitsError

from sciit import IssueRepo
from sciit.cli.functions import read_sciit_version
from sciit.cli.close_issue import close_issue
from sciit.cli.color import ColorPrint, ColorText
from sciit.cli.init import init
from sciit.cli.log import log
from sciit.cli.new_issue import new_issue
from sciit.cli.status import status
from sciit.cli.tracker import tracker
from sciit.cli.issue import issue
from sciit.cli.web import web
from sciit.gitlab.webservice import launch as launchgitlab


def add_revision_option(parser):
    parser.add_argument(
        'revision', action='store', type=str, nargs='?',
        help=
        'The revision path to use to generate the issue log e.g \'all\' for all commits or \'master\' for all commit on'
        ' master branch or \'HEAD~2\' from the last two commits on current branch. See git rev-list options for more '
        'path options.')


def add_new_issue_options(parser):
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-p', '--push', help='Pushes the newly created issue branch to the origin.', action='store_true')
    group.add_argument(
        '-a', '--accept', help='Accepts the newly created issue branch by merging it to master locally.', action='store_true')


def add_issue_filter_options(parser):
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-a', '--all', help='show all the issues currently tracked and their status', action='store_true')
    group.add_argument(
        '-o', '--open', help=ColorText.green('default:') + ' show only issues that are open', action='store_true')
    group.add_argument('-c', '--closed', help='show only issues that are closed', action='store_true')


def add_view_options(parser):
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-f', '--full', action='store_true',
        help=
        'view the full tracker information for all issues including, description revisions, commit activity, '
        'issue revisions, multiple file paths, open in, and found in branches ')
    group.add_argument(
        '-n', '--normal', action='store_true',
        help=ColorText.green('default:') + ' view tracker information normally needed.')


def create_command_parser():

    parser = argparse.ArgumentParser(
        prog='git sciit',
        description=
        'To use the application you can create your issues anywhere in your source code as block comments in a '
        'particular format and it will become a trackable versioned object within your git environment. Operations '
        'done with git will run git sciit in the background in order to automate issue tracking for you. '
    )
    parser.add_argument('-v', '--version', action='version', version=read_sciit_version())

    subparsers = parser.add_subparsers()

    init_parser = subparsers.add_parser(
        name='init',
        description=
        'Helps create an empty issue repository or build and issue repository from source code comments in past commits'
    )
    init_parser.set_defaults(func=init)
    init_parser.add_argument(
        '-r', '--reset', action='store_true', help='resets the issue repo and rebuild from past commits')

    status_parser = subparsers.add_parser(
        name='status',
        description=
        'Shows the user how many issues are open and how many are closed on all branches.'
    )
    status_parser.set_defaults(func=status)
    add_revision_option(status_parser)
    add_view_options(status_parser)

    log_parser = subparsers.add_parser(
        'log', description='Prints a log that is similar to the git log but shows open issues')
    log_parser.set_defaults(func=log)

    add_revision_option(log_parser)

    tracker_parser = subparsers.add_parser('tracker', description='Prints a log that shows issues and their status.')
    tracker_parser.set_defaults(func=tracker)
    add_revision_option(tracker_parser)

    add_issue_filter_options(tracker_parser)
    add_view_options(tracker_parser)

    issue_parser = subparsers.add_parser('issue', description='Prints an issue and it\'s status')
    issue_parser.set_defaults(func=issue)

    add_view_options(issue_parser)

    issue_parser.add_argument(
        'issue_id', action='store', type=str,
        help='The id of the issue that you are looking for')

    add_revision_option(issue_parser)

    web_parser = subparsers.add_parser(
        'web',
        description='Launches a local web interface for the sciit issue tracker')
    web_parser.set_defaults(func=web)

    gitlab_parser = subparsers.add_parser(
        'gitlab', description='Launches the gitlab webservice that integrates gitlab issues with sciit')
    gitlab_parser.set_defaults(func=launchgitlab)

    new_parser = subparsers.add_parser(
        'new',
        description='Creates a new issue in the project backlog on a branch specified by the issue id.')
    new_parser.set_defaults(func=new_issue)

    add_new_issue_options(new_parser)

    close_parser = subparsers.add_parser(
        'close',
        description='Closes an issue in the current branch.')
    close_parser.set_defaults(func=close_issue)

    close_parser.add_argument(
        'issue_id', action='store', type=str,
        help='The id of the issue to be closed.')

    return parser


def main():
    parser = create_command_parser()
    args = parser.parse_args()
    print(dir(args))
    try:
        git_repository = Repo(search_parent_directories=True)
        repo = IssueRepo(git_repository)
        repo.cli = True
        colorama.init()
        if not hasattr(args, 'func'):
            parser.print_help()
        else:
            args.repo = repo
            if args.func == init:
                args.func(args)
            else:
                if not args.repo.is_init():
                    ColorPrint.red('Repository not initialized')
                    ColorPrint.bold_red('Run: git sciit init')
                else:
                    args.func(args)

        # Forces proper clean up of git repository resources on Windows.
        # See https://github.com/gitpython-developers/GitPython/issues/508
        git_repository.__del__()

    except InvalidGitRepositoryError:
        ColorPrint.bold('fatal: not a git repository (or any parent up to mount point /)')
        ColorPrint.bold('Stopping at filesystem boundary(GIT_DISCOVERY_ACROSS_FILESYSTEM not set).')
    except NoCommitsError as error:
        ColorPrint.bold_red(f'git sciit error fatal: {str(error)}')
    except GitCommandError:
        ColorPrint.bold_red(f'git sciit error fatal: bad git command')
    except RepoObjectDoesNotExistError as error:
        ColorPrint.bold_red(error)
        print('Solve error by rebuilding issue repository using: git sciit init -r')


def start():
    if __name__ == '__main__':
        sys.exit(main())


start()
