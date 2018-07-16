# -*- coding: utf-8 -*-
"""Module that assists with running git issue tracker commands.
This is in no way similar to any other git command. It compares
all tracked issues with issues open in the current HEAD or branch.

    Example:
        This module is accessed via::

            $ git issue tracker [-h] [--all] [--open] [--closed] [branch]

@author: Nystrom Edwards

Created on 10 July 2018
"""

from gitissue.cli.functions import page_history_items
from gitissue.errors import NoCommitsError


def tracker(args):
    """
    Prints a log that shows issues and their status based on the 
    flags specified
    """
    # supresses open if other flags supplied
    if args.all or args.closed:
        args.open = False

    try:
        # open flag selected
        if args.open and not args.all and not args.closed:
            history = args.repo.open_issues
        # all flag selected
        elif args.all and not args.closed and not args.open:
            history = args.repo.all_issues
        # closed flag selected
        elif args.closed and not args.open and not args.all:
            history = args.repo.closed_issues
        if history:
            page_history_items(history)
        else:
            print('No issues found')
    except NoCommitsError as error:
        error = 'git issue error fatal: ' + str(error)
        print(error)
        return
