# -*- coding: utf-8 -*-
"""Module that assists with creating a git issue repository.
It contains functions that allows the creation of an empty
repository or to create a repository from source code comments
in past commits. It is similar to the git init command but 
helps build issues for existing repositories.

    Example:
        This command is accessed via::
        
            $ git issue init [-h] [-r] [-y]

@author: Nystrom Edwards

Created on 18 June 2018
"""

import sys
from gitissue.cli.functions import yes_no_option
from gitissue.errors import EmptyRepositoryError, NoCommitsError
from termcolor import colored


def init(args):
    """
    Helps create an empty issue repository or build and issue 
    repository from source code comments in past commits
    """
    if args.reset:
        try:
            args.repo.reset()
        except EmptyRepositoryError as error:
            print(error)

    """
    @issue 1
    @title Create Post Commit Scripts for Caching Changes to Issues
    """

    if not args.repo.is_init():
        args.repo.setup()

        if args.yes or yes_no_option('Build issue repository from past commits'):
            try:
                print(' ')
                print('Building repository from commits')
                args.repo.build()
                print(' ')
            except NoCommitsError as error:
                print(error)
                print('Empty issue repository created')
            except KeyboardInterrupt:
                print('\n')
                print(colored('Setup issue repository process interupted', 'red'))
                print('Cleaning up')
                args.repo.reset()
                print(colored('Done.', 'green') +
                      ' Re-run command to setup repository')
                sys.exit(0)
        else:
            print('Empty issue repository created')
    else:
        print('Issue repository already setup')

    return
