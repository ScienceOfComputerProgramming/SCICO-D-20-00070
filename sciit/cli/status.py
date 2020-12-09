# -*- coding: utf-8 -*-

from sciit.cli.functions import build_status_table, build_status_summary, page


def status(args):
    revision = args.revision if args.revision else None
    issue_repository = args.repo
    if args.normal:
        issues = issue_repository.get_all_issues(revision)
    elif args.all:
        issues = issue_repository.get_all_issues(revision)
    elif args.closed:
        issues = issue_repository.get_closed_issues(revision)
    else:
        issues = issue_repository.get_open_issues(revision)

    if args.full:
        page(build_status_table(issue_repository, issues))
    else:
        page(build_status_summary(issue_repository, revision))
