# -*- coding: utf-8 -*-
"""Module that assists with running git sciit issue commands.
This is in no way similar to any other git command. It gets the
issue tracking information for a particular issue specified by the
user.

    Example:
        This module is accessed via::

            $ git sciit issue [-h] [-f | -d | -n] [--save] issueid [*revision*]

@author: Nystrom Edwards

Created on 10 July 2018
"""
from sciit.cli.functions import page_history_item
from sciit.cli.color import CPrint
from slugify import slugify


def issue(args):
    """
    Prints an issue and its status based on the
    issue-id specified
    """
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
    history = args.repo.build_history(args.revision)
    if args.issueid in history:
        return page_history_item(history[args.issueid], view)
    else:
        if history:
            CPrint.bold_red(
                f'No issues found matching \'{args.issueid}\' ')
            print('\nHere are issues that are in the tracker:\n')
            print("\n".join(history.keys()))
        else:
            CPrint.bold_red(
                f'No issues in the repository')
