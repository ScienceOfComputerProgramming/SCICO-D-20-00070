# -*- coding: utf-8 -*-
"""Module that assists with running git sciit tracker commands.
This is in no way similar to any other git command. It compares
all tracked issues with issues open in the current repository 
or from the specified revision revision.

    Example:
        This module is accessed via::

            $ git sciit tracker [-h] [--all] [--open] [--closed] [revision]

@author: Nystrom Edwards

Created on 10 July 2018
"""
from git.exc import GitCommandError
from sciit.cli.functions import page_history_items
from sciit.errors import NoCommitsError
from sciit.functions import cache_history
from termcolor import colored


def tracker(args):
    """
    Prints a log that shows issues and their status based on the
    flags specified
    """
    if not args.repo.is_init():
        print(colored('Repository not initialized', 'red') + '\n' +
              colored('Run: git scitt init', 'red', attrs=['bold']))
        return

    args.repo.sync()
    # force open if no flags supplied
    if not args.all and not args.closed and not args.open:
        args.open = True

    try:
        # open flag selected
        if args.open:
            history = args.repo.get_open_issues(args.revision)
        # all flag selected
        elif args.all:
            history = args.repo.get_all_issues(args.revision)
        # closed flag selected
        elif args.closed:
            history = args.repo.get_closed_issues(args.revision)
        if history:
            if args.save:
                cache_history(args.repo.issue_dir, history)
                print('Issues saved to ' + args.repo.issue_dir + '/HISTORY\n')
            else:
                page_history_items(history)
        else:
            print(colored('No issues found', 'green', attrs=['bold']))
    except NoCommitsError as error:
        error = f'git sciit error fatal: {str(error)}'
        print(colored(error, 'red', attrs=['bold']))
        return
    except GitCommandError as error:
        error = f'git sciit error fatal: bad revision \'{args.revision}\''
        print(colored(error, 'red', attrs=['bold']))
        return
