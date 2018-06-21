# -*- coding: utf-8 -*-
"""Module that provides tools for the terminal.

:@author: Nystrom Edwards
:Created: 13 June 2018
"""
import os
import subprocess
import pkg_resources
from git import Repo


def is_init():
    """
    A function that is used to detect if the git-issue folders
    are initialised

    Returns:
        :bool: true if folder exists, false otherwise
    """
    repo = Repo()
    issue_dir = repo.git_dir + '/issue'
    return os.path.exists(issue_dir)


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


def run_command(cmd):
    """
    A function used for running commands within shell.

    Returns:
        :str: contains the result of the stdout produced by the shell command
    """
    output = subprocess.run(cmd.split(), stdout=subprocess.PIPE)
    output = output.stdout.decode('utf-8')
    return output


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
