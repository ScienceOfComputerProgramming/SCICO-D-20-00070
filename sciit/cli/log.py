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

from sciit.cli.functions import page_log
from sciit.cli.color import CPrint


def log(args):
    """
    Prints a log that is similar to the git log but shows open issues
    """
    if args.revision:
        revision = args.revision
    else:
        revision = args.repo.head

    args.repo.sync()
    all_issue_commits = list(args.repo.iter_issue_commits(revision))
    output = page_log(all_issue_commits)
    return output
