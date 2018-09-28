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


def subheader(header):
    return Color.bold(f'\n{header}')


def build_history_item(item, view=None):
    """
    Builds a string representation of a issue history item for showing to the terminal with ANSI color codes

    Args:
        :(dict) item: item to build string from

    Returns:
        :(str): string representation of issue history item
    """

    status = item.status
    participants = ', '.join(item.participants)

    output = ''
    output += f'\nTitle:             ' + Color.bold_yellow(f"{item.title}")
    output += f'\nID:                {item.issue_id}'
    output += f'\nStatus:            ' + (Color.red(status) if status == 'Open' else Color.green(status))
    output += f'\n'
    output += f'\nClosed:            {item.closer} | {item.closed_date}' if item.closer else ''
    output += f'\nLast Authored:     {item.last_author} | {item.last_authored_date}'
    output += f'\nCreated:           {item.creator} | {item.created_date}'
    output += f'\n'
    output += f'\nAssigned To:       {item.assignees}' if item.assignees else ''
    output += f'\nParticipants:      {participants}'
    output += f'\nDue Date:          {item.due_date}' if item.due_date else ''
    output += f'\nLabels:            {item.label}' if item.label else ''
    output += f'\nWeight:            {item.weight}' if item.weight else ''
    output += f'\nPriority:          {item.priority}' if item.priority else ''

    if view == 'full' or view == 'detailed':
        branches = ', '.join(item.in_branches)
        output += f'\nExisted in:        {branches}'

    output += f'\nSize:              {str(item.size)}' if item.size else ''
    output += f'\nLatest file path:  {item.file_paths[0]["file_path"]}' if len(item.file_paths) > 0 else ''

    if item.status == 'Open' and (view == 'full' or view == 'detailed') and len(item.file_paths) > 1:
        output += "\nOther branch file paths:\n"
        for path in item.file_paths[1:]:
            branch_status = 'open' if path['branch'] in item.open_in else 'closed'
            output += f'\n                   {path["file_path"]} @{path["branch"]} ({branch_status})'

    if item.description:
        output += f'\nDescription:'
        output += '\n' if not item.description.startswith('\n') else ''
        output += item.description

    if view == 'full':
        num_revisions = str(len(item.revisions))
        output += subheader(f'\nRevisions to Issue ({num_revisions}):\n')

        for revision in item.revisions:

            changes = revision['changes']
            output += f'\nIn {revision["issuesha"]} ({len(changes)} items changed):\n'

            for changed_property, new_value in changes.items():
                output += f' {changed_property}: {new_value}\n'

            output += f'\n'
            output += f'{Color.bold_yellow("--> made by: " + revision["author"])} - {revision["date"]}\n'

    if view == 'full' or view == 'detailed':
        num_commits = str(len(item.activity))
        output += subheader(f'\nPresent in Commits ({num_commits}):')
        for commit in item.activity:
            output += f'\n{commit["date"]}'
            if view == 'full':
                output += f' | {commit["commitsha"]} | {commit["author"]} | {commit["summary"]}'

    output += f'\n{Color.yellow("*"*90)}\n'

    return output
