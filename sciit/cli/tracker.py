# -*- coding: utf-8 -*-

import datetime
from sciit.cli import build_issue_history, page, ProgressTracker
from sciit.cli.color import Styling


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
        print(Styling.error_warning('No issues found'))


def page_history_issues(history, view=None, issue_filter=None):

    filtered_history = list(filter(issue_filter, history.values()))
    filtered_history.sort(key=lambda issue: issue.last_authored_date, reverse=True)
    num_issues = len(filtered_history)
    current_issue = 0
    output = ''

    progress_tracker = ProgressTracker(num_issues, object_type_name='issues')

    for item in filtered_history:
        if issue_filter is None or issue_filter(item):
            output += build_issue_history(item, view)
            current_issue += 1

            progress_tracker.processed_object()

    page(output)
    return output
