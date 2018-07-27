# -*- coding: utf-8 -*-
"""Module that assists printing objects to the terminal, getting
terminal responses from user input, and getting contents of
static files contained in the package

@author: Nystrom Edwards

Created on 10 July 2018
"""
import pydoc
import pkg_resources
from termcolor import colored


def page(output):
    pydoc.pipepager(output, cmd='less -FRSX')


def build_log_item(icommit):
    """Builds a string representation of issue commit for log
    to the terminal

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
    to the terminal

    Args:
        :list(IssueCommit) icommits: commits to build string from

    Returns:
        :(str): string representation of issue commit for log
    """
    output = ''
    for icommit in icommits:
        output += build_log_item(icommit)
    return output


def page_log(icommits):
    """Prints raw string output to less pager

    Args:
        :list(IssueCommit) icommits: commits to print to pager
    """
    output = build_log(icommits)
    page(output)
    return output


def build_issue_commit(icommit):
    """Builds a string representation of issue commit for showing
    to the terminal

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


def page_issue_commit(icommit):
    """Prints raw string output to less pager

    Args:
        :(IssueCommit) icommit: commit to print to pager
    """
    output = build_issue_commit(icommit)
    page(output)
    return output


def build_issue_tree(itree):
    """Builds a string representation of issue tree for showing
    to the terminal

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


def page_issue_tree(itree):
    """Prints raw string output to less pager

    Args:
        :(IssueTree) itree: issue tree to print to pager
    """
    output = build_issue_tree(itree)
    page(output)
    return output


def build_issue(issue):
    """Builds a string representation of issue for showing
    to the terminal

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


def page_issue(issue):
    """Prints raw string output to less pager

    Args:
        :(Issue) issue: issue to print to pager
    """
    output = build_issue(issue)
    page(output)
    return output


def build_history_item(item):
    """Builds a string representation of a issue history item for showing
    to the terminal

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
    output += f'\nIn Branches:        '
    for branch in item['in_branches']:
        output += branch + ', '
    output += f'\nOpen In Branches:   '
    for branch in item['open_in']:
        output += branch + ', '
    if 'size' in item:
        output += f'\nSize:               {str(item["size"])}'
    output += '\nFilepath:'
    for path in item['filepath']:
        output += '\n' + ' '*20 + path

    output += f'\n'
    output += f'\nIssue Revisions:    {str(len(item["revisions"]))}'
    for revision in item['revisions']:
        output += '\n' + ' '*20 + revision

    output += f'\n'
    output += f'\nCommit Activities:  {str(len(item["activity"]))}'
    for commit in item['activity']:
        output += f'\n{commit["date"]}'
        output += f' | {commit["author"]}'
        output += f' | {commit["summary"]}'

    output += f'\n'
    if 'description' in item:
        output += '\n' + '_'*90 + '\n' + Color.bold('Descriptions:')
        for description in item['descriptions']:
            output += f'\n{description["change"]}'
            output += f'\n--> added by:'
            output += f' {Color.red(description["author"])}'
            output += f' - {description["date"]}'
            output += '\n' + '_'*70

    output += f'\n\n'
    output += f'{Color.yellow("*"*90)}'
    output += f'\n\n'
    return output


def page_history_item(item):
    """Prints raw string output to less pager

    Args:
        :(dict) item: history_item to print to pager
    """
    output = build_history_item(item)
    page(output)
    return output


def build_history_items(items):
    """Builds a string representation of a dict of history items
    for showing to the terminal

    Args:
        :dict(dict) items: history items to build string from

    Returns:
        :(str): string representation of history items
    """
    output = ''
    for item in items.values():
        output += build_history_item(item)
    return output


def page_history_items(items):
    """Prints raw string output to less pager

    Args:
        :dict(dict) items: history items to print to pager
    """
    output = build_history_items(items)
    page(output)
    return output


def yes_no_option(msg=''):
    """
    A function used to stall program operation until user
    specifies an option of yes or no

    Returns:
        :bool: True if user enters y or Y
        :bool: False if user enter otherwise
    """
    option = input(msg + ' [y/N]: ')
    if option is 'Y' or option is 'y':
        return True
    else:
        return False


def read_man_file(filename):
    """
    A function used for accessing the manual page files stored in
    the src/man folder.

    Returns:
        :str: The contents of the file
    """
    filename = pkg_resources.resource_filename('sciit.man', filename)
    with open(filename, 'rb') as f:
        filename = f.read().decode('utf-8')
    return filename


def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=50, fill='█'):
    """
    Used in the command line application.
    Call in a loop to create terminal progress bar
    from https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console

    Args:
       :(int) iteration: current iteration
       :(int) total: total iterations
       :(str) prefix: prefix string
       :(str) suffix: suffix string
       :(str) decimals: positive number of decimals in percent complete
       :(int) length: character length of bar
       :(str) fill: bar fill character
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 *
                                                     (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end='\r')
    # Print New Line on Complete
    if iteration == total:
        print()


class Color:
    """A simple class wrapper that helps to add color to strings
    """

    @classmethod
    def red(cls, string):
        return(colored(string, 'red'))

    @classmethod
    def green(cls, string):
        return(colored(string, 'green'))

    @classmethod
    def yellow(cls, string):
        return(colored(string, 'yellow'))

    @classmethod
    def bold(cls, string):
        return(colored(string, attrs=['bold']))

    @classmethod
    def bold_red(cls, string):
        return(colored(string, 'red', attrs=['bold']))

    @classmethod
    def bold_green(cls, string):
        return(colored(string, 'green', attrs=['bold']))

    @classmethod
    def bold_yellow(cls, string):
        return(colored(string, 'yellow', attrs=['bold']))


class CPrint:
    """A simple class wrapper that helps to print messages to the
    shell terminals
    """

    @classmethod
    def red(cls, string):
        print(colored(string, 'red'))

    @classmethod
    def green(cls, string):
        print(colored(string, 'green'))

    @classmethod
    def yellow(cls, string):
        print(colored(string, 'yellow'))

    @classmethod
    def bold(cls, string):
        print(colored(string, attrs=['bold']))

    @classmethod
    def bold_red(cls, string):
        print(colored(string, 'red', attrs=['bold']))

    @classmethod
    def bold_green(cls, string):
        print(colored(string, 'green', attrs=['bold']))

    @classmethod
    def bold_yellow(cls, string):
        print(colored(string, 'yellow', attrs=['bold']))
