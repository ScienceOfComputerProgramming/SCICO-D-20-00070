# -*- coding: utf-8 -*-
"""Module that provides main() entry point of the command 
line interface that accepts the command line arguments and 
pass them to the appropriate module for handling.

    Example:
        This module is accessed via::
        
            $ git issue

@author: Nystrom Edwards

Created on 13 June 2018
"""

import argparse
import sys

from gitissue.tools.system import read_man_file

from gitissue.status import status
from gitissue.init import init
from gitissue.log import log

from git import Repo
from git.exc import InvalidGitRepositoryError


def main():
    """The function that provides an entry point for the cli application.
    The ```ArgumentParser``` is the main component responsible for 
    interpreting the command line arguments. The subparsers are responsible
    for reading the sub components of the sub arguments.
    """
    try:
        repo = Repo()

        parser = argparse.ArgumentParser(description='')
        parser.add_argument('-v', '--version', action='version',
                            version=read_man_file('VERSION'))

        subparsers = parser.add_subparsers()

        # responsible for the init subcommand
        init_parser = subparsers.add_parser('init')
        init_parser.set_defaults(func=init)
        init_parser.add_argument('-r', '--reset', action='store_true',
                                 help='resets the issue repo and allows rebuild from commits')

        # responsible for the status subcommand
        status_parser = subparsers.add_parser('status')
        status_parser.set_defaults(func=status)

        # responsible for the log subcommand
        log_parser = subparsers.add_parser('log')
        log_parser.set_defaults(func=log)

        # allow the cli to run if we are in a legal .git repo
        if repo.git_dir:
            args = parser.parse_args()

            # no args supplied
            if not len(sys.argv) > 1:
                parser.print_help()
            else:
                args.func(args)
                sys.exit(0)
    except InvalidGitRepositoryError:
        print('fatal: not a git repository (or any parent up to mount point /)')
        print('Stopping at filesystem boundary(GIT_DISCOVERY_ACROSS_FILESYSTEM not set).')
        sys.exit(0)


if __name__ == '__main__':
    main()
