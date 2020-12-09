# -*- coding: utf-8 -*-

from sciit.cli.styling import Styling
from sciit.cli.functions import page, build_issue_history


def issue(args):

    issue = args.repo.get_issue(args.issue_id, args.revision)

    if issue is not None:
        view = 'full' if args.full else 'normal'
        return page_history_issue(issue, view)
    else:
        issue_keys = args.repo.get_issue_keys()
        if len(issue_keys) > 0:
            print(Styling.error_warning(f'No issues found matching \'{args.issue_id}\' '))
            print('\nHere are issues that are in the tracker:\n')
            print("\n".join(issue_keys))
        else:
            print(Styling.error_warning(f'No issues in the repository.'))
        return ""


def page_history_issue(item, view=None):
    output = build_issue_history(item, view)
    page(output)
    return output
