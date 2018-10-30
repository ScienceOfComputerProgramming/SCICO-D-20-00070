# -*- coding: utf-8 -*-
"""
Assists with running git sciit status commands, and is similar to the git status command but shows the status of issues
that are currently being tracked on HEAD or revision.
"""

from sciit.cli.functions import print_status_table


def status(args):
    revision = args.revision if args.revision else None
    issue_repository = args.repo
    print_status_table(issue_repository, revision)
