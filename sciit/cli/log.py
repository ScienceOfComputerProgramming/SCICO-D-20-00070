# -*- coding: utf-8 -*-
"""Module that assists with running git sciit log commands.
It is similar to the git log command but shows the open 
issues for each commit.

    Example:
        This command is accessed via:
        
            $ git sciit log [-h] [revision]

@author: Nystrom Edwards

Created on 18 June 2018
"""

from git.exc import GitCommandError
from sciit.cli.functions import page_log, CPrint


def log(args):
    """
    Prints a log that is similar to the git log but shows open issues
    """
    if not args.repo.is_init():
        CPrint.red('Repository not initialized')
        CPrint.bold_red('Run: git scitt init')
        return

    args.repo.sync()
    if args.revision:
        revision = args.revision
    else:
        revision = args.repo.head

    try:
        all_issue_commits = list(args.repo.iter_issue_commits(revision))
        output = page_log(all_issue_commits)
    # if user enters incorrect value for revision
    except GitCommandError as e:
        error = e.stderr.replace('\n\'', '')
        error = error.replace('\n  stderr: \'', '')
        error = 'git sciit error ' + error
        CPrint.bold_red(error)
        return
    return output
