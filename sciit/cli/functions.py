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


def build_log_item(icommit):
    """Builds a string representation of issue commit for log 
    to the terminal

    Args:
        :(IssueCommit) icommit: commit to build string from

    Returns:
        :(str): string representation of issue commit for log
    """
    time_format = '%a %b %d %H:%M:%S %Y %z'
    output = ''
    date = icommit.commit.authored_datetime.strftime(time_format)
    output +=  \
        colored(f'commit {icommit.hexsha} ', 'yellow') + \
        f'\nAuthor:\t {icommit.commit.author.name} <{icommit.commit.author.email}>' + \
        f'\nDate:\t {date}' + \
        f'\n' + colored(f'Open Issues: {icommit.open_issues}', 'red') + \
        f'\n' + \
        f'\n{icommit.commit.message}' + \
        f'\n'
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


def print_log(icommits):
    """Prints raw string output to stdout

    Args:
        :list(IssueCommit) icommits: commits to print to stdout
    """
    output = build_log(icommits)
    print(output)


def page_log(icommits):
    """Prints raw string output to less pager

    Args:
        :list(IssueCommit) icommits: commits to print to pager
    """
    output = build_log(icommits)
    pydoc.pipepager(output, cmd='less -R')


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
    output = 'tree ' + icommit.commit.tree.hexsha + \
        '\nissuetree ' + icommit.issuetree.hexsha + \
        '\nopen issues: ' + str(icommit.open_issues)
    for parent in icommit.commit.parents:
        output += '\nparent ' + parent.hexsha
    output += '\nauthor ' + icommit.commit.author.name + \
        ' <' + icommit.commit.author.email + '> ' \
        + str(icommit.commit.authored_date) + ' ' + atime + \
        '\ncommiter ' + icommit.commit.committer.name + \
        ' <' + icommit.commit.committer.email + '> ' + \
        str(icommit.commit.committed_date) + ' ' + ctime + \
        '\n\n' + \
        icommit.commit.message + '\n'
    return output


def print_issue_commit(icommit):
    """Prints raw string output to stdout

    Args:
        :(IssueCommit) icommit: commit to print to stdout
    """
    output = build_issue_commit(icommit)
    print(output)


def page_issue_commit(icommit):
    """Prints raw string output to less pager

    Args:
        :(IssueCommit) icommit: commit to print to pager
    """
    output = build_issue_commit(icommit)
    pydoc.pipepager(output, cmd='less -R')


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
        if hasattr(issue, 'title'):
            title = issue.title
        else:
            title = colored('No title', 'red')
        output += issue.id + '\t' + \
            issue.hexsha + '\t' + \
            title + '\t' + issue.filepath + '\n'
    return output


def print_issue_tree(itree):
    """Prints raw string output to stdout

    Args:
        :(IssueTree) itree: issue tree to print to stdout
    """
    output = build_issue_tree(itree)
    print(output)


def page_issue_tree(itree):
    """Prints raw string output to less pager

    Args:
        :(IssueTree) itree: issue tree to print to pager
    """
    output = build_issue_tree(itree)
    pydoc.pipepager(output, cmd='less -R')


def build_issue(issue):
    """Builds a string representation of issue for showing 
    to the terminal

    Args:
        :(Issue) issue: issue to build string from

    Returns:
        :(str): string representation of issue
    """
    output = ''
    if hasattr(issue, 'id'):
        output += colored('Issue: ' + issue.id, 'yellow')
    if hasattr(issue, 'status'):
        output += '\n'
        if issue.status == 'Open':
            output += colored('Status: ' + issue.status, 'red')
        else:
            output += colored('Status: ' + issue.status, 'green')
    if hasattr(issue, 'title'):
        output += '\nTitle:         ' + issue.title
    if hasattr(issue, 'assignees'):
        output += '\nAssigned To:   ' + issue.assignees
    if hasattr(issue, 'due_date'):
        output += '\nDue Date:      ' + issue.due_date
    if hasattr(issue, 'label'):
        output += '\nLabels:        ' + issue.label
    if hasattr(issue, 'weight'):
        output += '\nWeight:        ' + issue.weight
    if hasattr(issue, 'priority'):
        output += '\nPriority:      ' + issue.priority
    if hasattr(issue, 'filepath'):
        output += '\nFilepath:      ' + issue.filepath
    if hasattr(issue, 'size'):
        output += '\nSize:          ' + str(issue.size)
    if hasattr(issue, 'description'):
        output += '\nDescription: ' + issue.description
    output += '\n\n'
    return output


def print_issue(issue):
    """Prints raw string output to stdout

    Args:
        :(Issue) issue: issue to print to stdout
    """
    output = build_issue(issue)
    print(output)


def page_issue(issue):
    """Prints raw string output to less pager

    Args:
        :(Issue) issue: issue to print to pager
    """
    output = build_issue(issue)
    pydoc.pipepager(output, cmd='less -R')


def build_issues(issues):
    """Builds a string representation of a list fo issues for showing 
    to the terminal

    Args:
        :list(Issue) issues: issues to build string from

    Returns:
        :(str): string representation of issues
    """
    output = ''
    for issue in issues:
        output += build_issue(issue)
    return output


def print_issues(issues):
    """Prints raw string output to stdout

    Args:
        :list(Issue) issues: issues to print to stdout
    """
    output = build_issues(issues)
    print(output)


def page_issues(issues):
    """Prints raw string output to less pager

    Args:
        :list(Issue) issues: issues to print to pager
    """
    output = build_issues(issues)
    pydoc.pipepager(output, cmd='less -R')


def build_history_item(item):
    """Builds a string representation of a issue history item for showing 
    to the terminal

    Args:
        :(dict) item: item to build string from

    Returns:
        :(str): string representation of issue history item
    """
    output = ''
    output += colored('ID: ' + item['id'], 'yellow', attrs=['bold'])
    output += '\n'
    if item['status'] == 'Open':
        output += colored('Status: ' + item['status'], 'red', attrs=['bold'])
    else:
        output += colored('Status: ' + item['status'], 'green', attrs=['bold'])
    output += '\nTitle: ' + item['title']

    output += '\n'
    output += '\nLast Authored:      ' + \
        item['last_author'] + ' | ' + \
        item['last_authored_date']
    output += '\nCreated:            ' +\
        item['creator'] + ' | ' + \
        item['created_date']
    output += '\n'

    if 'assignees' in item:
        output += '\nAssigned To:        ' + item['assignees']
    output += '\nParticipants:       '
    for participant in item['participants']:
        output += participant + ','
    if 'due_date' in item:
        output += '\nDue Date:           ' + item['due_date']
    if 'label' in item:
        output += '\nLabels:             ' + item['label']
    if 'weight' in item:
        output += '\nWeight:             ' + item['weight']
    if 'priority' in item:
        output += '\nPriority:           ' + item['priority']
    output += '\nIn Branches:        '
    for branch in item['in_branches']:
        output += branch + ', '
    output += '\nOpen In Branches:   '
    for branch in item['open_in']:
        output += branch + ', '
    if 'size' in item:
        output += '\nSize:               ' + str(item['size'])
    output += '\nFilepath:'
    for path in item['filepath']:
        output += '\n' + ' '*20 + path

    output += '\n'
    output += '\nIssue Revisions:    ' + str(len(item['revisions']))
    for revision in item['revisions']:
        output += '\n' + ' '*20 + revision

    output += '\n'
    output += '\nCommit Activities:  ' + str(len(item['activity']))
    for commit in item['activity']:
        output += '\n' + commit['date']
        output += ' | ' + commit['author']
        output += ' | ' + commit['summary']

    output += '\n'
    if 'description' in item:
        output += '\n' + '_'*90 + '\n' + 'Descriptions:'
        for description in item['descriptions']:
            output += '\n' + description['change']
            output += '\n--> added by: ' + \
                colored(description['author'], 'red')
            output += ' - ' + description['date']
            output += '\n' + '_'*70

    output += '\n\n'
    output += colored('*'*90, 'yellow')
    output += '\n\n'
    return output


def print_history_item(item):
    """Prints raw string output to stdout

    Args:
        :(dict) item: history_item to print to stdout
    """
    output = build_history_item(item)
    print(output)


def page_history_item(item):
    """Prints raw string output to less pager

    Args:
        :(dict) item: history_item to print to pager
    """
    output = build_history_item(item)
    pydoc.pipepager(output, cmd='less -R')


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


def print_history_items(items):
    """Prints raw string output to stdout

    Args:
        :dict(dict) items: history items to print to stdout
    """
    output = build_history_items(items)
    print(output)


def page_history_items(items):
    """Prints raw string output to less pager

    Args:
        :dict(dict) items: history items to print to pager
    """
    output = build_history_items(items)
    pydoc.pipepager(output, cmd='less -R')


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
