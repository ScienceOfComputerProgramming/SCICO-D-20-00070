# -*- coding: utf-8 -*-
"""Module that provides main() entry point of the command 
line interface that accepts the command line arguments and 
pass them to the appropriate module for handling.

    Example:
        This command is accessed via::
        
            $ git sciit

@author: Nystrom Edwards

Created on 13 June 2018
"""

import argparse
import sys
import colorama

from git.exc import InvalidGitRepositoryError

from sciit import IssueRepo
from sciit.cli.catfile import catfile
from sciit.cli.functions import read_man_file
from sciit.cli.color import CPrint, Color
from sciit.cli.init import init
from sciit.cli.log import log
from sciit.cli.status import status
from sciit.cli.tracker import tracker
from sciit.cli.issue import issue
from sciit.web.server import launch


def main():
    """The function that provides an entry point for the cli application.
    The ```ArgumentParser``` is the main component responsible for 
    interpreting the command line arguments. The subparsers are responsible
    for reading the sub components of the sub arguments.
    """
    try:
        repo = IssueRepo()
        repo.cli = True
        colorama.init()  # initialise colours for windows

        parser = argparse.ArgumentParser(prog='git sciit',
                                         description='To use the application you can create your '
                                         'issues anywhere in your source code as block comments in '
                                         'a particular format and it will become a trackable '
                                         'versioned object within your git environment. '
                                         'Operations done with git will run git sciit in the '
                                         'background in order to automate issue tracking for you. ')
        parser.add_argument('-v', '--version', action='version',
                            version=read_man_file('VERSION'))

        subparsers = parser.add_subparsers()

        # responsible for the init subcommand
        init_parser = subparsers.add_parser('init', description=' Helps create an empty issue repository'
                                            ' or build and issue repository from source code comments in'
                                            ' past commits')
        init_parser.set_defaults(func=init)
        init_parser.add_argument('-r', '--reset', action='store_true',
                                 help='resets the issue repo and rebuild from past commits')

        # responsible for the status subcommand
        status_parser = subparsers.add_parser('status', description='Shows the user how many issues are open'
                                              ' and how many are closed on all branches.')
        status_parser.set_defaults(func=status)
        status_parser.add_argument('revision', action='store', type=str, nargs='?',
                                   help='the revision path to use to generate the issue log e.g \'all\' '
                                   'for all commits or \'master\' for all commit on master branch '
                                   'or \'HEAD~2\' from the last two commits on current branch. '
                                   'see git rev-list options for more path options.')

        # responsible for the log subcommand
        log_parser = subparsers.add_parser('log', description='Prints a log that is similar to the git'
                                           ' log but shows open issues')
        log_parser.set_defaults(func=log)
        log_parser.add_argument('revision', action='store', type=str, nargs='?',
                                help='the revision path to use to generate the issue log e.g \'all\' '
                                'for all commits or \'master\' for all commit on master branch '
                                'or \'HEAD~2\' from the last two commits on current branch. '
                                'see git rev-list options for more path options.')

        # responsible for the cat-file subcommand
        cat_file_parser = subparsers.add_parser('cat-file', description='Prints the content and info of objects'
                                                ' stored in our issue repository. Only one flag can be specified')
        cat_file_parser.set_defaults(func=catfile)
        cat_file_parser.add_argument('sha', action='store', type=str,
                                     help='the sha of the issue repository object')
        group = cat_file_parser.add_mutually_exclusive_group(required=True)
        group.add_argument('-t', '--type', action='store_true',
                           help='instead of the content, show the object type identified by <object>.')
        group.add_argument('-s', '--size', action='store_true',
                           help='instead of the content, show the object size identified by <object>.')
        group.add_argument('-p', '--print', action='store_true',
                           help='pretty prints the contents of <object> based on type')

        # responsible for the tracker subcommand
        tracker_parser = subparsers.add_parser(
            'tracker', description='Prints a log that shows issues and their status')
        tracker_parser.set_defaults(func=tracker)
        tracker_parser.add_argument('revision', action='store', type=str, nargs='?',
                                    help='default: uses the entire issue repository. or if'
                                    'specified the revision which you would like '
                                    'to check for your issue tracker. see git revision '
                                    'for more information *optional')
        group = tracker_parser.add_mutually_exclusive_group()
        group.add_argument('-a', '--all',
                           help='show all the issues currently tracked and their status',
                           action='store_true')
        group.add_argument('-o', '--open',
                           help=Color.green('default:') +
                           ' show only issues that are open',
                           action='store_true')
        group.add_argument('-c', '--closed',
                           help='show only issues that are closed',
                           action='store_true')
        group2 = tracker_parser.add_mutually_exclusive_group()
        group2.add_argument('-f', '--full',
                            help='view the full tracker information for all issues including, '
                            'description revisions, commit activity, issue revisions, '
                            'multiple filepaths, open in, and found in branches  ',
                            action='store_true')
        group2.add_argument('-d', '--detailed',
                            help='view tracker information including '
                            'commit activity, multiple filepaths, open in, '
                            'and found in branches ',
                            action='store_true')
        group2.add_argument('-n', '--normal',
                            help=Color.green('default:') +
                            ' view tracker information normally needed ',
                            action='store_true')
        tracker_parser.add_argument('-s', '--save', action='store_true',
                                    help='saves issue history selected to the HISTORY file in '
                                    'your issue repository directory')

        # responsible for the issue subcommand
        issue_parser = subparsers.add_parser(
            'issue', description='Prints an issue and it\'s status')
        issue_parser.set_defaults(func=issue)
        group = issue_parser.add_mutually_exclusive_group()
        group.add_argument('-f', '--full',
                           help='view the full tracker information for all issues including, '
                           'description revisions, commit activity, issue revisions, '
                           'multiple filepaths, open in, and found in branches  ',
                           action='store_true')
        group.add_argument('-d', '--detailed',
                           help='view tracker information including '
                           'commit activity, multiple filepaths, open in, '
                           'and found in branches ',
                           action='store_true')
        group.add_argument('-n', '--normal',
                           help=Color.green('default:') +
                           ' view tracker information normally needed ',
                           action='store_true')
        issue_parser.add_argument('issueid', action='store', type=str,
                                  help='The id of the issue that you are looking for')
        issue_parser.add_argument('-s', '--save', action='store_true',
                                  help='saves issue history selected to the HISTORY file in '
                                  'your issue repository directory')
        issue_parser.add_argument('revision', action='store', type=str, nargs='?',
                                  help='the revision path to use to generate the issue log e.g \'all\' '
                                  'for all commits or \'master\' for all commit on master branch '
                                  'or \'HEAD~2\' from the last two commits on current branch. '
                                  'see git rev-list options for more path options. *optional')

        # responsible for launching the local web server
        web_parser = subparsers.add_parser(
            'web', description='Launches the web interface')
        web_parser.set_defaults(func=launch)

        args = parser.parse_args()

        # no args supplied
        if not hasattr(args, 'func'):
            parser.print_help()
        else:
            args.repo = repo
            args.func(args)
        return
    except InvalidGitRepositoryError:
        CPrint.bold(
            'fatal: not a git repository (or any parent up to mount point /)')
        CPrint.bold(
            'Stopping at filesystem boundary(GIT_DISCOVERY_ACROSS_FILESYSTEM not set).')
        return


def start():
    if __name__ == '__main__':
        sys.exit(main())


start()
