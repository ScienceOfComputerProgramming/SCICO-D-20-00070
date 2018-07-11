# -*- coding: utf-8 -*-
"""Module that assists with running git issue log commands.
It is similar to the git log command but shows the open 
issues for each commit.

    Example:
        This command is accessed via:
        
            $ git issue log [-h] [revision]

@author: Nystrom Edwards

Created on 18 June 2018
"""
from git.exc import GitCommandError
from gitissue.cli.functions import page_log


def log(args):
    """
    Prints a log that is similar to the git log but shows open issues
    """

    if args.revision:
        if args.revision == 'all':
            revision = '--' + args.revision
        else:
            revision = args.revision
    else:
        revision = args.repo.head

    all_issue_commits = args.repo.iter_issue_commits(revision)

    try:
        page_log(all_issue_commits)
    # if user enters incorrect value for revision
    except GitCommandError as e:
        error = e.stderr.replace('\n\'', '')
        error = error.replace('\n  stderr: \'', '')
        error = 'git issue error ' + error
        print(error)
        return
    return
