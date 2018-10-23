# -*- coding: utf-8 -*-
"""
Implements the git sciit issue commands. Issue tracking information is retrieved for a particular issue.

    Example:
        This module is accessed via::

            $ git sciit issue [-h] [-f | -d | -n] [--save] issueid [*revision*]
"""

import datetime

from sciit.cli.color import CPrint, Color
from sciit.cli.functions import page, print_progress_bar


def issue(args):

    if not args.normal and not args.detailed and not args.full:
        args.normal = True

    if args.normal:
        view = 'normal'
    elif args.detailed:
        view = 'detailed'
    elif args.full:
        view = 'full'

    args.repo.cache_issue_snapshots_from_unprocessed_commits()

    history = args.repo.build_history(args.revision)

    if args.issue_id in history:
        return page_history_issue(history[args.issue_id], view)
    else:
        if history:
            CPrint.bold_red(f'No issues found matching \'{args.issue_id}\' ')
            print('\nHere are issues that are in the tracker:\n')
            print("\n".join(history.keys()))
        else:
            CPrint.bold_red(f'No issues in the repository')

def page_history_issue(item, view=None):
    output = build_issue_history(item, view)
    page(output)
    return output


def page_history_issues(items, view=None, issue_filter=None):

    filtered_items = list(filter(issue_filter, items.values()))

    start = datetime.datetime.now()
    num_issues = len(filtered_items)
    cur_issue = 0
    output = ''

    for item in filtered_items:
        if issue_filter is None or issue_filter(item):
            output += build_issue_history(item, view, items)
            cur_issue += 1
            duration = datetime.datetime.now() - start
            prefix = 'Recovering %d/%d issues: ' % (cur_issue, num_issues)
            suffix = ' Duration: %s' % str(duration)

            print_progress_bar(cur_issue, num_issues, prefix, suffix)

    page(output)
    return output


def subheader(header):
    return Color.bold(f'\n{header}')


def build_issue_history(issue_item, view=None, other_issue_items=dict()):
    """
    Builds a string representation of a issue history item for showing to the terminal with ANSI color codes

    Args:
        :(dict) item: item to build string from

    Returns:
        :(str): string representation of issue history item
    """
    status, sub_status = issue_item.status
    status_str = f'{status} ({sub_status})'

    participants = ', '.join(issue_item.participants)

    output = ''
    output += f'\nTitle:             ' + Color.bold_yellow(f"{issue_item.title}")
    output += f'\nID:                {issue_item.issue_id}'
    output += f'\nStatus:            ' + (Color.green(status_str) if status == 'Closed' else Color.red(status_str))
    output += f'\n'
    output += f'\nClosed:            {issue_item.closer} | {issue_item.closed_date}' if issue_item.closer else ''
    output += f'\nLast Change:       {issue_item.last_author} | {issue_item.last_authored_date}'
    output += f'\nCreated:           {issue_item.creator} | {issue_item.created_date}'
    output += f'\n'
    output += f'\nAssigned To:       {issue_item.assignees}' if issue_item.assignees else ''

    output += f'\nParticipants:      {participants}'
    output += f'\nDue Date:          {issue_item.due_date}' if issue_item.due_date else ''
    output += f'\nLabels:            {issue_item.label}' if issue_item.label else ''
    output += f'\nWeight:            {issue_item.weight}' if issue_item.weight else ''
    output += f'\nPriority:          {issue_item.priority}' if issue_item.priority else ''

    blocker_issues = issue_item.blockers

    if len(blocker_issues) > 0:
        blockers_status = list()
        for blocker_issue_id, blocker_issue in blocker_issues.items():
            blocker_status = blocker_issue.status[0] if blocker_issue is not None else '?'
            blockers_status.append('%s(%s)' % (blocker_issue_id,blocker_status))

        blockers_str = ', '.join(blockers_status)
        output += f'\nBlockers:          {blockers_str}'

    if view == 'full' or view == 'detailed':
        branches = ', '.join(issue_item.in_branches)
        output += f'\nExisted in:        {branches}'

    output += f'\nSize:              {str(issue_item.size)}' if issue_item.size else ''
    output += f'\nLatest file path:  {issue_item.file_path}' if len(issue_item.file_paths) > 0 else ''

    if (view == 'full' or view == 'detailed') and len(issue_item.file_paths) > 0:
        output += "\nBranch file paths:\n"
        for branch, path in issue_item.file_paths.items():
            branch_status = 'open' if branch in issue_item.open_in_branches else 'closed'
            output += f'\n                   {path} @{branch} ({branch_status})'

    if issue_item.description:
        output += f'\n\nDescription:'
        output += '\n' if not issue_item.description.startswith('\n') else ''
        output += issue_item.description

    if view == 'full':
        num_revisions = str(len(issue_item.revisions))
        output += subheader(f'\nRevisions to Issue ({num_revisions}):\n')

        for revision in issue_item.revisions:

            changes = revision['changes']
            output += f'\nIn {revision["commitsha"]} ({len(changes)} items changed):\n'

            for changed_property, new_value in changes.items():
                output += f' {changed_property}: {new_value}\n'

            output += f'\n'
            output += f'{Color.bold_yellow("--> made by: " + revision["author"])} - {revision["date"]}\n'
            output += f'    {revision["summary"]}\n'

    if view == 'full' or view == 'detailed':
        num_commits = str(len(issue_item.activity))
        output += subheader(f'\nPresent in Commits ({num_commits}):')
        for commit in issue_item.activity:
            output += f'\n{commit["date"]}'
            if view == 'full':
                output += f' | {commit["commitsha"]} | {commit["author"]} | {commit["summary"]}'

    output += f'\n{Color.yellow("*"*90)}\n'

    return output
