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
from sciit.cli.functions import CPrint


def status(args):
    """Shows the user information related to their open issues.
    """
    if not args.repo.is_init():
        CPrint.red('Repository not initialized')
        CPrint.bold_red('Run: git scitt init')
        return

    args.repo.sync()
    all_issues = args.repo.all_issues

    opened = sum(x['status'] == 'Open' for x in all_issues.values())
    closed = len(all_issues) - opened
    CPrint.bold_red(f'Open Issues: ' + str(opened))

    # TODO add a function to have closed issues
    CPrint.bold_green(f'Closed Issues: ' + str(closed))
    print('')
    return
