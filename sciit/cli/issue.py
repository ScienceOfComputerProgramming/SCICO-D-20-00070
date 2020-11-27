# -*- coding: utf-8 -*-

from sciit.cli.styling import Styling
from sciit.cli.functions import page, build_issue_history


def issue(args):

    issue = args.repo.get_issue(args.revision, args.issue_id)

    if issue is not None:
        view = 'full' if args.full else 'normal'
        return page_history_issue(issue, view)
    else:
        print(Styling.error_warning(f'No issues found matching \'{args.issue_id}\' '))
        # print('\nHere are issues that are in the tracker:\n')
        # print("\n".join(history.keys()))
        return ""


def page_history_issue(item, view=None):
    output = build_issue_history(item, view)
    page(output)
    return output
