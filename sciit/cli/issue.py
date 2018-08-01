# -*- coding: utf-8 -*-
"""Module that assists with running git sciit issue commands.
This is in no way similar to any other git command. It gets the
issue tracking information for a particular issue specified by the
user.

    Example:
        This module is accessed via::

            $ git sciit issue [-h] [issue-id]

@author: Nystrom Edwards

Created on 10 July 2018
"""
from git.exc import GitCommandError
from sciit.cli.functions import page_history_item
from sciit.cli.color import CPrint
from sciit.errors import NoCommitsError


def issue(args):
    """
    Prints an issue and its status based on the
    issue-id specified
    """
    if not args.repo.is_init():
        CPrint.red('Repository not initialized')
        CPrint.bold_red('Run: git scitt init')
        return

    args.repo.sync()
    try:
        history = args.repo.build_history()
        if args.issueid in history:
            page_history_item(history[args.issueid])
        else:
            print("\n".join(history.keys()))
            CPrint.bold_green('No issues found')
    except NoCommitsError as error:
        error = f'git sciit error fatal: {str(error)}'
        CPrint.bold_red(error)
        return
    except GitCommandError as error:
        error = f'git sciit error fatal: bad revision \'{args.revision}\''
        CPrint.bold_red(error)
        return
