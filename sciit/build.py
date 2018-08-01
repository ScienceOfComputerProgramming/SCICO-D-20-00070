# -*- coding: utf-8 -*-
"""Module that assists building strings containing the 
issue tracker information needed for showing to the user.

@author: Nystrom Edwards

Created on 29 July 2018
"""
import re
from sciit.cli.color import Color


def build_log_item(icommit):
    """Builds a string representation of issue commit for log
    to the terminal with ANSI color codes

    Args:
        :(IssueCommit) icommit: commit to build string from

    Returns:
        :(str): string representation of issue commit for log
    """
    time_format = '%a %b %d %H:%M:%S %Y %z'
    date = icommit.commit.authored_datetime.strftime(time_format)
    output = Color.bold_yellow(f'commit {icommit.hexsha}')
    output += f'\nAuthor:\t {icommit.commit.author.name} <{icommit.commit.author.email}>'
    output += f'\nDate:\t {date}'
    output += f'\n{Color.bold_red(f"Open Issues: {icommit.open_issues}")}'
    output += f'\n'
    output += f'\n{icommit.commit.message}'
    output += f'\n'
    return output


def build_log(icommits):
    """Builds a string representation of a list of issue commits for log
    to the terminal with ANSI color codes

    Args:
        :list(IssueCommit) icommits: commits to build string from

    Returns:
        :(str): string representation of issue commit for log
    """
    output = ''
    for icommit in icommits:
        output += build_log_item(icommit)
    return output


def build_clean_log(icommits):
    """Builds a string representation of a list of issue commits for log
    to the terminal without the ANSI color codes

    Args:
        :list(IssueCommit) icommits: commits to build string from

    Returns:
        :(str): string representation of issue commit for log
    """
    output = build_log(icommits)
    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    output = ansi_escape.sub('', output)
    return output


def build_issue_commit(icommit):
    """Builds a string representation of issue commit for showing
    to the terminal without ANSI color codes

    Args:
        :(IssueCommit) icommit: commit to build string from

    Returns:
        :(str): string representation of issue commit
    """
    time_format = '%z'
    atime = icommit.commit.authored_datetime.strftime(time_format)
    ctime = icommit.commit.committed_datetime.strftime(time_format)
    output = f'tree {icommit.commit.tree.hexsha}'
    output += f'\nissuetree {icommit.issuetree.hexsha}'
    output += f'\nopen issues: {str(icommit.open_issues)}'
    for parent in icommit.commit.parents:
        output += f'\nparent {parent.hexsha}'
    output += f'\nauthor {icommit.commit.author.name}'
    output += f' <{icommit.commit.author.email}>'
    output += f' {str(icommit.commit.authored_date)} {atime}'
    output += f'\ncommiter {icommit.commit.committer.name}'
    output += f' <{icommit.commit.committer.email}>'
    output += f' {str(icommit.commit.committed_date)} {ctime}'
    output += f'\n\n'
    output += f'{icommit.commit.message}\n'
    return output


def build_issue_tree(itree):
    """Builds a string representation of issue tree for showing
    to the terminal without ANSI color codes

    Args:
        :(IssueTree) itree: issue tree to build string from

    Returns:
        :(str): string representation of issue tree
    """
    output = ''
    for issue in itree.issues:
        title = issue.title
        output += f'{issue.id}\t'
        output += f'{issue.hexsha}\t'
        output += f'{title}\t'
        output += f'{issue.filepath}\n'
    return output


def build_issue(issue):
    """Builds a string representation of issue for showing
    to the terminal with ANSI color codes

    Args:
        :(Issue) issue: issue to build string from

    Returns:
        :(str): string representation of issue
    """
    output = f'{Color.bold_yellow(f"Issue:         {issue.id}")}'
    output += f'\nTitle:         {issue.title}'
    if hasattr(issue, 'assignees'):
        output += f'\nAssigned To:   {issue.assignees}'
    if hasattr(issue, 'due_date'):
        output += f'\nDue Date:      {issue.due_date}'
    if hasattr(issue, 'label'):
        output += f'\nLabels:        {issue.label}'
    if hasattr(issue, 'weight'):
        output += f'\nWeight:        {issue.weight}'
    if hasattr(issue, 'priority'):
        output += f'\nPriority:      {issue.priority}'
    if hasattr(issue, 'filepath'):
        output += f'\nFilepath:      {issue.filepath}'
    if hasattr(issue, 'size'):
        output += f'\nSize:          {str(issue.size)}'
    if hasattr(issue, 'description'):
        output += f'\nDescription: \n{issue.description}'
    output += f'\n\n'
    return output


def build_clean_issue(issue):
    """Builds a string representation of issue for showing
    to the terminal without ANSI color codes

    Args:
        :(Issue) issue: issue to build string from

    Returns:
        :(str): string representation of issue
    """
    output = build_issue(issue)
    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    output = ansi_escape.sub('', output)
    return output


def build_history_item(item, view=None):
    """Builds a string representation of a issue history item for showing
    to the terminal with ANSI color codes

    Args:
        :(dict) item: item to build string from

    Returns:
        :(str): string representation of issue history item
    """
    output = Color.bold_yellow(f"ID: {item['id']}")
    output += f'\n'
    status = item['status']
    if item['status'] == 'Open':
        output += f'{Color.red(f"Status: {status}")}'
    else:
        output += f'{Color.green(f"Status: {status}")}'
    output += f'\nTitle: {item["title"]}'

    output += f'\n'
    if 'closer' in item:
        output += f'\nClosed:             '
        output += f' {item["closer"]}'
        output += f' | {item["closed_date"]}'
    output += f'\nLast Authored:      '
    output += f' {item["last_author"]}'
    output += f' | {item["last_authored_date"]}'
    output += f'\nCreated:            '
    output += f' {item["creator"]}'
    output += f' | {item["created_date"]}'
    output += f'\n'

    if 'assignees' in item:
        output += f'\nAssigned To:        {item["assignees"]}'
    output += f'\nParticipants:       '
    for participant in item['participants']:
        output += participant + ', '
    if 'due_date' in item:
        output += f'\nDue Date:           {item["due_date"]}'
    if 'label' in item:
        output += f'\nLabels:             {item["label"]}'
    if 'weight' in item:
        output += f'\nWeight:             {item["weight"]}'
    if 'priority' in item:
        output += f'\nPriority:           {item["priority"]}'

    if view == 'full' or view == 'detailed':
        output += f'\nFound In:           '
        for branch in item['in_branches']:
            output += branch + ', '

    if item['status'] == 'Open':

        if view == 'full' or view == 'detailed':
            output += f'\nOpen In Branches:   '
            for branch in item['open_in']:
                output += branch + ', '

        if 'size' in item:
            output += f'\nSize:               {str(item["size"])}'
        if view == 'full' or view == 'detailed':
            output += '\nFilepaths:'
            for path in item['filepaths']:
                output += '\n' + ' '*20 + path
        else:
            output += '\nFilepath:           ' + item['filepath']

    if view == 'full':
        output += f'\n'
        output += f'\nIssue Revisions:    {str(len(item["revisions"]))}'
        for revision in item['revisions']:
            output += '\n' + revision

    if view == 'full' or view == 'detailed':
        output += f'\n'
        output += f'\nCommit Activities:  {str(len(item["activity"]))}'
        for commit in item['activity']:
            output += f'\n{commit["date"]}'
            output += f' | {commit["author"]}'
            output += f' | {commit["summary"]}'

    if view == 'full':
        output += f'\n'
        if 'descriptions' in item:
            output += '\n' + '_'*90 + '\n' + Color.bold('Descriptions:')
            for description in item['descriptions']:
                for line in description["change"].splitlines():
                    if line.startswith('+'):
                        output += '\n' + Color.green(line)
                    elif line.startswith('-'):
                        output += '\n' + Color.red(line)
                    elif line.startswith('?'):
                        output += '\n' + Color.yellow(line)
                    else:
                        output += '\n' + line
                output += f'\n\n'
                output += f'{Color.bold_yellow("--> added by: " + description["author"])}'
                output += f' - {description["date"]}'
                output += '\n' + '_'*70
    else:
        output += f'\n'
        if 'description' in item:
            output += '\n' + '_'*90 + '\n' + Color.bold('Description:')
            output += '\n' + item['description']
            output += f'\n\n'
            output += f'{Color.bold_yellow("--> added by: " + item["last_author"])}'
            output += f' - {item["last_authored_date"]}'
            output += '\n' + '_'*70

    output += f'\n\n'
    output += f'{Color.yellow("*"*90)}'
    output += f'\n\n'
    return output


def build_history_items(items, view=None):
    """Builds a string representation of a dict of history items
    for showing to the terminal with ANSI color codes

    Args:
        :dict(dict) items: history items to build string from

    Returns:
        :(str): string representation of history items
    """
    output = ''
    for item in items.values():
        output += build_history_item(item, view)
    return output


def build_clean_history_items(items):
    """Builds a string representation of a dict of history items
    for showing to the terminal without ANSI color codes

    Args:
        :dict(dict) items: history items to build string from

    Returns:
        :(str): string representation of history items
    """
    output = build_history_items(items)
    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    output = ansi_escape.sub('', output)
    return output
