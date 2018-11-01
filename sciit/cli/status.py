# -*- coding: utf-8 -*-
"""
Assists with running git sciit status commands, and is similar to the git status command but shows the status of issues
that are currently being tracked on HEAD or revision.
"""

from sciit.cli.functions import build_status_table, build_status_summary, page


def status(args):
    revision = args.revision if args.revision else None
    issue_repository = args.repo
    if args.full:
        page(build_status_table(issue_repository, revision))
    else:
        page(build_status_summary(issue_repository, revision))
