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
from slugify import slugify


def issue(args):
    """
    Prints an issue and its status based on the
    issue-id specified
    """
    if not args.repo.is_init():
        CPrint.red('Repository not initialized')
        CPrint.bold_red('Run: git scitt init')
        return

    # force normal if no flags supplied
    if not args.normal and not args.detailed and not args.full:
        args.normal = True

    if args.normal:
        view = 'normal'
    elif args.detailed:
        view = 'detailed'
    elif args.full:
        view = 'full'

    args.repo.sync()
    args.issueid = slugify(args.issueid)
    try:
        history = args.repo.build_history()
        if args.issueid in history:
            page_history_item(history[args.issueid], view)
        else:
            CPrint.bold_red(f'No issues found matching \'{args.issueid}\' ')
            print('\nHere are issues that are in the tracker:\n')
            print("\n".join(history.keys()))
    except NoCommitsError as error:
        error = f'git sciit error fatal: {str(error)}'
        CPrint.bold_red(error)
        return
    except GitCommandError as error:
        error = f'git sciit error fatal: bad revision \'{args.revision}\''
        CPrint.bold_red(error)
        return
