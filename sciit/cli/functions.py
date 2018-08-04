# -*- coding: utf-8 -*-
"""Module that assists printing objects to the terminal, getting
terminal responses from user input, and getting contents of
static files contained in the package

@author: Nystrom Edwards

Created on 10 July 2018
"""
import pydoc
import pkg_resources
from sciit.build import (build_log, build_issue_commit, build_issue_tree,
                         build_issue, build_history_item, build_history_items)


def page(output):
    pydoc.pipepager(output, cmd='less -FRSX')


def page_log(icommits):
    """Prints raw string output to less pager

    Args:
        :list(IssueCommit) icommits: commits to print to pager
    """
    output = build_log(icommits)
    page(output)
    return output


def page_issue_commit(icommit):
    """Prints raw string output to less pager

    Args:
        :(IssueCommit) icommit: commit to print to pager
    """
    output = build_issue_commit(icommit)
    page(output)
    return output


def page_issue_tree(itree):
    """Prints raw string output to less pager

    Args:
        :(IssueTree) itree: issue tree to print to pager
    """
    output = build_issue_tree(itree)
    page(output)
    return output


def page_issue(issue):
    """Prints raw string output to less pager

    Args:
        :(Issue) issue: issue to print to pager
    """
    output = build_issue(issue)
    page(output)
    return output


def page_history_item(item, view=None):
    """Prints raw string output to less pager

    Args:
        :(dict) item: history_item to print to pager
    """
    output = build_history_item(item, view)
    page(output)
    return output


def page_history_items(items, view=None):
    """Prints raw string output to less pager

    Args:
        :dict(dict) items: history items to print to pager
    """
    output = build_history_items(items, view)
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
