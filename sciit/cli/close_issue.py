# -*- coding: utf-8 -*-

from sciit.cli.functions import do_repository_has_no_commits_warning, build_issue_history, page

from sciit.write_commit import close_issue as _close_issue


def close_issue(args):

    issue_repository = args.repo
    git_repository = issue_repository.git_repository

    if not git_repository.heads:
        do_repository_has_no_commits_warning()
        return

    issue_id = args.issue_id

    issue = issue_repository.get_issue(issue_id)

    _close_issue(issue_repository, issue, branch_names=[issue_id])

    print('Done\n')
    issue = issue_repository.get_issue(issue_id)
    page(build_issue_history(issue))
