# -*- coding: utf-8 -*-
"""
Assists with running git sciit tracker commands, and is similar to any other git command. It compares
all tracked issues with issues open in the current repository or from the specified revision.

"""
from sciit.cli.issue import page_history_issues
from sciit.cli.color import ColorPrint


def tracker(args):

    if not args.all and not args.closed and not args.open:
        args.open = True

    if args.full:
        view = 'full'
    else:
        view = 'normal'

    history = args.repo.get_all_issues(args.revision)
    if history:
        if args.open:
            return page_history_issues(history, view, lambda issue: issue.status[0] == 'Open')
        elif args.all:
            return page_history_issues(history, view, lambda issue: True)
        elif args.closed:
            return page_history_issues(history, view, lambda issue: issue.status[0] == 'Closed')
    else:
        ColorPrint.bold_green('No issues found')
