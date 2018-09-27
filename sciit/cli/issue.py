# -*- coding: utf-8 -*-
"""
Implements the git sciit issue commands. Issue tracking information is retrieved for a particular issue.

    Example:
        This module is accessed via::

            $ git sciit issue [-h] [-f | -d | -n] [--save] issueid [*revision*]
"""

from sciit.cli.color import CPrint, Color
from slugify import slugify
from sciit.cli.functions import page


def issue(args):

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
            CPrint.bold_red(f'No issues found matching \'{args.issueid}\' ')
            print('\nHere are issues that are in the tracker:\n')
            print("\n".join(history.keys()))
        else:
            CPrint.bold_red(f'No issues in the repository')


def page_history_item(item, view=None):
    output = build_history_item(item, view)
    page(output)
    return output


def page_history_items(items, view=None):
    output = ''
    for item in items.values():
        output += build_history_item(item, view)

    page(output)
    return output


def build_history_item(item, view=None):
    """
    Builds a string representation of a issue history item for showing to the terminal with ANSI color codes

    Args:
        :(dict) item: item to build string from

    Returns:
        :(str): string representation of issue history item
    """

    output = Color.bold_yellow(f"ID: {item.issue_id}")
    output += f'\n'

    status = item.status

    if status == 'Open':
        output += f'{Color.red(f"Status: {status}")}'
    else:
        output += f'{Color.green(f"Status: {status}")}'

    output += f'\nTitle: {item.title}'

    output += f'\n'

    if item.closer:
        output += f'\nClosed:             '
        output += f' {item.closer}'
        output += f' | {item.closed_date}'

    output += f'\nLast Authored:      '
    output += f' {item.last_author}'
    output += f' | {item.last_authored_date}'
    output += f'\nCreated:            '
    output += f' {item.creator}'
    output += f' | {item.created_date}'
    output += f'\n'

    if item.assignees:
        output += f'\nAssigned To:        {item.assignees}'

    output += f'\nParticipants:       '

    for participant in item.participants:
        output += participant + ', '
    if item.due_date:
        output += f'\nDue Date:           {item.due_date}'
    if item.label:
        output += f'\nLabels:             {item.label}'
    if item.weight:
        output += f'\nWeight:             {item.weight}'
    if item.priority:
        output += f'\nPriority:           {item.priority}'

    if view == 'full' or view == 'detailed':
        output += f'\nFound In:           '
        for branch in item.in_branches:
            output += '\n' + ' '*20 + branch

    if item.size:
        output += f'\nSize:               {str(item.size)}'

    if len(item.file_paths) > 0:
        output += '\nFile path:         ' + item.file_paths[0]['file_path']

    if item.status == 'Open':

        if view == 'full' or view == 'detailed':

            output += f'\nOpen In Branches:   '
            for branch in item.open_in:
                output += '\n' + ' '*20 + branch

            output += '\nFile paths:'
            for path in item.file_paths:
                output += '\n' + ' '*20 + path['file_path'] + ' @' + path['branch']

    if view == 'full':
        output += f'\n'
        output += f'\nIssue Revisions:    {str(len(item.revisions))}'
        for revision in item.revisions:
            output += '\n' + revision['issuesha']
            if 'changes' in revision:
                output += ' changes: '
                for change in revision['changes']:
                    output += f'{change}, '

    if view == 'full' or view == 'detailed':
        output += f'\n'
        output += f'\nCommit Activities:  {str(len(item.activity))}'
        for commit in item.activity:
            output += f'\n{commit["date"]}'
            if view == 'full':
                output += f' | {commit["commitsha"]}'
            output += f' | {commit["author"]}'
            output += f' | {commit["summary"]}'

    if view == 'full':
        output += f'\n'
        if item.descriptions:
            output += '\n' + '_'*90 + '\n' + Color.bold('Descriptions:')
            for description in item.descriptions:
                for line in description["change"].splitlines():
                    if line.startswith('+'):
                        output += '\n' + Color.green(line)
                    elif line.startswith('-'):
                        output += '\n' + Color.red(line)
                    else:
                        output += '\n' + line
                output += f'\n\n'
                output += f'{Color.bold_yellow("--> added by: " + description["author"])}'
                output += f' - {description["date"]}'
                output += '\n' + '_'*70
    else:
        output += f'\n'
        if item.description:
            output += '\n' + '_'*90 + '\n' + Color.bold('Description:')
            output += '\n' + item.description
            output += f'\n\n'
            output += f'{Color.bold_yellow("--> added by: " + item.last_author)}'
            output += f' - {item.last_authored_date}'
            output += '\n' + '_'*70

    output += f'\n\n'
    output += f'{Color.yellow("*"*90)}'
    output += f'\n\n'
    return output
