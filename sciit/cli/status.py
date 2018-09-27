# -*- coding: utf-8 -*-
"""Module that assists with running git sciit status commands.
It is similar to the git status command but shows the status
of issues that are currently being tracked on HEAD or revision.

    Example:
        This command is accessed via::

            $ git sciit status [-h] [revision]

@author: Nystrom Edwards

Created on 13 June 2018
"""
from git.exc import GitCommandError
from sciit.errors import RepoObjectDoesNotExistError
from sciit import IssueCommit
from sciit.cli.color import CPrint


def status(args):
    """Shows the user information related to their open issues.
    """
    if args.revision:
        revision = args.revision
    else:
        revision = args.repo.head
   
    args.repo.sync()
    all_issues = args.repo.get_all_issues(revision)
    opened = sum(issue.status == 'Open' for issue in all_issues.values())
    closed = len(all_issues) - opened
    CPrint.bold_red(f'Open Issues: ' + str(opened))
    CPrint.bold_green(f'Closed Issues: ' + str(closed))
    print('')
    return
