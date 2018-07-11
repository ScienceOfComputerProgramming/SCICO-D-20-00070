# -*- coding: utf-8 -*-
"""Module that assists with running git issue status commands.
It is similar to the git status command but shows the status
of issues that are currently being tracked on HEAD or branch.

    Example:
        This command is accessed via::

            $ git issue status [-h] [branch]

@author: Nystrom Edwards

Created on 13 June 2018
"""
from gitissue import IssueCommit
from gitissue.repo import get_all_issues
from termcolor import colored


def status(args):
    """Shows the user information related to their open issues.
    """
    if args.branch:
        branch = args.branch
        print(f'For branch ' + branch)
    else:
        branch = args.repo.head.ref.name
        print(f'On branch ' + branch)

    try:
        all_issues = get_all_issues(args.repo, branch)
    except IndexError:
        error = 'git issue error fatal: No such branch matching ' + branch + ' found'
        print(error)
        return

    opened = sum(x.status == 'Open' for x in all_issues)
    closed = len(all_issues) - opened
    print(colored(f'Open Issues: ' + str(opened), 'red'))

    # TODO add a function to have closed issues
    print(colored(f'Closed Issues: ' + str(closed), 'green'))
    print('')
    return
