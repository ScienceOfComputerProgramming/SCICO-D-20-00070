# -*- coding: utf-8 -*-
"""Module that assists with running git sciit tracker commands.
This is in no way similar to any other git command. It compares
all tracked issues with issues open in the current HEAD or branch.

    Example:
        This module is accessed via::

            $ git sciit tracker [-h] [--all] [--open] [--closed] [branch]

@author: Nystrom Edwards

Created on 10 July 2018
"""

from sciit.cli.functions import page_history_items
from sciit.errors import NoCommitsError
from sciit.functions import cache_history


def tracker(args):
    """
    Prints a log that shows issues and their status based on the 
    flags specified
    """
    # force open if no flags supplied
    if not args.all and not args.closed and not args.open:
        args.open = True

    try:
        # open flag selected
        if args.open:
            history = args.repo.open_issues
        # all flag selected
        elif args.all:
            history = args.repo.all_issues
        # closed flag selected
        elif args.closed:
            history = args.repo.closed_issues
        if history:
            if args.save:
                cache_history(args.repo.issue_dir, history)
                print('Issue file saved to ./git/issue/HISTORY')
            else:
                page_history_items(history)
        else:
            print('No issues found')
    except NoCommitsError as error:
        error = 'git sciit error fatal: ' + str(error)
        print(error)
        return
