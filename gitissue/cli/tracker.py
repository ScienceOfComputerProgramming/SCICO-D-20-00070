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

from gitissue.repo import get_all_issues, get_open_issues, get_closed_issues
from gitissue.cli.functions import page_issues
from gitissue.errors import NoIssueHistoryError


def tracker(args):
    """
    Prints a log that shows issues and their status based on the 
    flags specified
    """
    # supresses open if other flags supplied
    if args.all or args.closed:
        args.open = False

    if hasattr(args, 'branch'):
        branch = args.branch
    else:
        branch = None

    try:
        # open flag selected
        if args.open and not args.all and not args.closed:
            issues = get_open_issues(args.repo, branch)
        # all flag selected
        elif args.all and not args.closed and not args.open:
            issues = get_all_issues(args.repo, branch)
        # closed flag selected
        elif args.closed and not args.open and not args.all:
            issues = get_closed_issues(args.repo, branch)
        if issues:
            page_issues(issues)
        else:
            print('No issues found')
    except NoIssueHistoryError as error:
        error = 'git issue error fatal: ' + str(error)
        print(error)
        return
    except IndexError:
        error = 'git issue error fatal: No such branch matching ' + branch + ' found'
        print(error)
        return
