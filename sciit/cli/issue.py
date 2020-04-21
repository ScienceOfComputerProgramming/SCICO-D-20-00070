# -*- coding: utf-8 -*-

from sciit.cli.color import Styling
from sciit.cli.functions import page, build_issue_history


def issue(args):

    if args.full:
        view = 'full'
    else:
        view = 'normal'

    history = args.repo.build_history(args.revision)

    if args.issue_id in history:
        return page_history_issue(history[args.issue_id], view)
    else:
        if history:
            print(Styling.error_warning(f'No issues found matching \'{args.issue_id}\' '))
            print('\nHere are issues that are in the tracker:\n')
            print("\n".join(history.keys()))
        else:
            print(Styling.error_warning(f'No issues in the repository'))
        return ""


def page_history_issue(item, view=None):
    output = build_issue_history(item, view)
    page(output)
    return output
