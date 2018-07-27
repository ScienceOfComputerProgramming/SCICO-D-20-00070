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
from sciit import IssueCommit
from sciit.cli.functions import CPrint


def status(args):
    """Shows the user information related to their open issues.
    """
    if not args.repo.is_init():
        CPrint.red('Repository not initialized')
        CPrint.bold_red('Run: git scitt init')
        return

    if args.revision:
        revision = args.revision
    else:
        revision = args.repo.head

    args.repo.sync()
    try:
        all_issues = args.repo.get_all_issues(revision)
    except GitCommandError as e:
        error = e.stderr.replace('\n\'', '')
        error = error.replace('\n  stderr: \'', '')
        error = 'git sciit error ' + error
        CPrint.bold_red(error)
        return

    opened = sum(x['status'] == 'Open' for x in all_issues.values())
    closed = len(all_issues) - opened
    CPrint.bold_red(f'Open Issues: ' + str(opened))

    # TODO add a function to have closed issues
    CPrint.bold_green(f'Closed Issues: ' + str(closed))
    print('')
    return
