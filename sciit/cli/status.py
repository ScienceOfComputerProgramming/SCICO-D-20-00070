# -*- coding: utf-8 -*-
"""Module that assists with running git sciit status commands.
It is similar to the git status command but shows the status
of issues that are currently being tracked on HEAD or branch.

    Example:
        This command is accessed via::

            $ git sciit status [-h] [branch]

@author: Nystrom Edwards

Created on 13 June 2018
"""
from sciit import IssueCommit
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
        all_issues = args.repo.all_issues
    except IndexError:
        error = 'git sciit error fatal: No such branch matching ' + branch + ' found'
        print(error)
        return

    opened = sum(x['status'] == 'Open' for x in all_issues.values())
    closed = len(all_issues) - opened
    print(colored(f'Open Issues: ' + str(opened), 'red'))

    # TODO add a function to have closed issues
    print(colored(f'Closed Issues: ' + str(closed), 'green'))
    print('')
    return
