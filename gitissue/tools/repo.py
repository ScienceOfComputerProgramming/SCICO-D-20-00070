# -*- coding: utf-8 -*-
"""Module that assists with running git commands at sys level.
It contains functions that when used get information output by 
git commands on stdout.

@author: Nystrom Edwards

Created on 13 June 2018
"""

import os
from gitissue.tools.system import run_command, read_man_file


def get_git_directory():
    """Determines if we are in a current .git repo

    Returns:
        bool: False if not in a .git repo

        string: The location of the .git repo folder
    """
    directory = get_src_directory()
    if not directory:
        return False
    else:
        return directory + '/.git'


def get_src_directory():
    """Determines if we are in a current .git repo and the 
    location of the top-level directory

    Returns:
        bool: False if there is an error from git command

        string: The location of the src directory
    """
    directory = run_command('git rev-parse --show-toplevel')
    if directory == "":
        return False
    else:
        return directory.strip('\r\n')


def get_git_remote_type():
    remotes = []
    output = run_command('git remote -v')
    supported = get_supported_repos()

    for repo in supported:
        if repo in output:
            remotes.append(repo)

    return remotes


def get_supported_repos():
    supported = read_man_file('SUPPORTED_REPOS')
    return supported.split('\n')


def get_repo_type_from_user():
    supported = get_supported_repos()
    option = input(
        'What type of repository is this ' + str(supported) + ' supported: ')
    if option in supported:
        return option
    else:
        return('ERROR: Unsupported repository')
