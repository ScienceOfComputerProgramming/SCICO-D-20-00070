# -*- coding: utf-8 -*-
"""Module that assists printing objects to the terminal.

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
    log = ''
    date = icommit.commit.authored_datetime.strftime(time_format)
    log = log + \
        colored(f'commit {icommit.hexsha} ', 'yellow') + \
        f'\nAuthor:\t {icommit.commit.author.name} <{icommit.commit.author.email}>' + \
        f'\nDate:\t {date}' + \
        f'\n' + colored(f'Open Issues: {icommit.open_issues}', 'red') + \
        f'\n' + \
        f'\n{icommit.commit.message}' + \
        f'\n'
    return log


def build_log(icommits):
    """Builds a string representation of a list of issue commits for log 
    to the terminal

    Args:
        :list(IssueCommit) icommits: commits to build string from

    Returns:
        :(str): string representation of issue commit for log
    """
    log = ''
    for icommit in icommits:
        log = log + build_log_item(icommit)
    return log


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
        output = output + '\nparent ' + parent.hexsha
    output = output + '\nauthor ' + icommit.commit.author.name + \
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
        output = output + issue.number + '\t' + \
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
    if hasattr(issue, 'number'):
        output = output + colored('Issue: ' + issue.number, 'yellow')
    if hasattr(issue, 'status'):
        output = output + '\n'
        if issue.status == 'Open':
            output = output + colored('Status: ' + issue.status, 'red')
        else:
            output = output + colored('Status: ' + issue.status, 'green')
    if hasattr(issue, 'title'):
        output = output + '\nTitle:         ' + issue.title
    if hasattr(issue, 'assignees'):
        output = output + '\nAssigned To:   ' + issue.assignees
    if hasattr(issue, 'due_date'):
        output = output + '\nDue Date:      ' + issue.due_date
    if hasattr(issue, 'label'):
        output = output + '\nLabels:        ' + issue.label
    if hasattr(issue, 'weight'):
        output = output + '\nWeight:        ' + issue.weight
    if hasattr(issue, 'priority'):
        output = output + '\nPriority:      ' + issue.priority
    if hasattr(issue, 'filepath'):
        output = output + '\nFilepath:      ' + issue.filepath
    if hasattr(issue, 'size'):
        output = output + '\nSize:          ' + str(issue.size)
    if hasattr(issue, 'description'):
        output = output + '\nDescription: ' + issue.description
    output = output + '\n\n'
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
        output = output + build_issue(issue)
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
    filename = pkg_resources.resource_filename('gitissue.man', filename)
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
