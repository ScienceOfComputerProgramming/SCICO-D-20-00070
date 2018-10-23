# -*- coding: utf-8 -*-
"""
Assists with running git sciit status commands, and is similar to the git status command but shows the status of issues
that are currently being tracked on HEAD or revision.

    Example:
        This command is accessed via::

            $ git sciit status [-h] [revision]
"""
from sciit.cli.color import CPrint
from sciit.cli.functions import print_status_summary

def status(args):
    revision = args.revision if args.revision else None

    args.repo.cache_issue_snapshots_from_unprocessed_commits()
    all_issues = args.repo.get_all_issues(revision)
    open = sum(issue.status[0] == 'Open' for issue in all_issues.values())
    closed = len(all_issues) - open
    CPrint.bold_red(f'Open Issues: ' + str(open))
    CPrint.bold_green(f'Closed Issues: ' + str(closed))
    print('')
    return
