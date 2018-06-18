# -*- coding: utf-8 -*-
"""Module that provides tools for the command line 
interface.

@author: Nystrom Edwards

Created on 13 June 2018
"""

import subprocess
import pkg_resources


def yes_no_option(msg=''):
    """
    A function used to stall program operation until user 
    specifies an option of yes or no

    Returns:
        bool: True if user enters y or Y

        bool: False if user enter otherwise
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
        string: contains the result of the stdout produced by 
        the shell command
    """
    output = subprocess.run(cmd.split(), stdout=subprocess.PIPE)
    output = output.stdout.decode('utf-8')
    return output


def read_man_file(filename):
    """
    A function used for accessing the manual page files stored in
    the src/man folder.

    Returns:
        string: The contents of the file
    """
    filename = pkg_resources.resource_filename('gitissue.man', filename)
    with open(filename, 'rb') as f:
        filename = f.read().decode('utf-8')
    return filename
