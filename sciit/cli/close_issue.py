# -*- coding: utf-8 -*-

from sciit.cli.functions import do_repository_has_no_commits_warning_and_exit, build_issue_history, page

from sciit.write_commit import close_issue as _close_issue


def _remove_issue_from_codebase(issue):
    file_path = issue.file_path
    start_position = issue.start_position
    end_position = issue.end_position

    with open(file_path, mode='r') as issue_file:
        file_content = issue_file.read()

    file_content_with_issue_removed = file_content[0:start_position] + file_content[end_position:]

    with open(file_path, mode='w') as issue_file:
        issue_file.write(file_content_with_issue_removed)


def close_issue(args):

    issue_repository = args.repo
    git_repository = issue_repository.git_repository

    if not git_repository.heads:
        do_repository_has_no_commits_warning_and_exit()
        return

    issue_id = args.issue_id

    issues = issue_repository.get_all_issues()
    issue = issues[issue_id]

    _close_issue(issue_repository, issue, 'master')

    print('Done\n')

    page(build_issue_history(issue, issues))
