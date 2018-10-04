# -*- coding: utf-8 -*-
"""
Assists with running git sciit status commands, and is similar to the git status command but shows the status of issues
that are currently being tracked on HEAD or revision.

    Example:
        This command is accessed via::

            $ git sciit status [-h] [revision]
"""
from sciit.cli.color import CPrint


def status(args):
    if args.revision:
        revision = args.revision
    else:
        revision = args.repo.head
   
    args.repo.sync()
    all_issues = args.repo.get_all_issues(revision)
    print(all_issues)
    opened = sum(issue.status == 'Open' for issue in all_issues.values())
    closed = len(all_issues) - opened
    CPrint.bold_red(f'Open Issues: ' + str(opened))
    CPrint.bold_green(f'Closed Issues: ' + str(closed))
    print('')
    return
