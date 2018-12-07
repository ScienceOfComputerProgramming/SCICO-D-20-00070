# -*- coding: utf-8 -*-
"""
Assists with running git sciit tracker commands, and is similar to any other git command. It compares
all tracked issues with issues open in the current repository or from the specified revision.

"""

import datetime
from sciit.cli.functions import build_issue_history, page, print_progress_bar
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


def page_history_issues(history, view=None, issue_filter=None):

    filtered_history = list(filter(issue_filter, history.values()))
    filtered_history.sort(key = lambda issue: issue.last_authored_date, reverse=True)
    start = datetime.datetime.now()
    num_issues = len(filtered_history)
    current_issue = 0
    output = ''

    for item in filtered_history:
        if issue_filter is None or issue_filter(item):
            output += build_issue_history(item, view)
            current_issue += 1
            duration = datetime.datetime.now() - start
            prefix = 'Recovering %d/%d issues:  ' % (current_issue, num_issues)
            suffix = ' Duration: %s' % str(duration)

            print_progress_bar(current_issue, num_issues, prefix, suffix)

    page(output)
    return output

