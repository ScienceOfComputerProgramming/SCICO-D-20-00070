import slugify
import os
from sciit.cli.functions import do_commit_contains_duplicate_issue_filepaths_check, build_issue_history, page
from sciit.cli.color import ColorPrint
from sciit.errors import NoCommitsError


def read_input_with_default(prompt, default):

    result = input("%s [%s]:" % (prompt, default)).rstrip('\r\n')

    return result if result != "" else default


def close_issue(args):

    issue_repository = args.repo
    git_repository = issue_repository.git_repository

    if not git_repository.heads:
        print(' ')
        ColorPrint.bold_red('The repository has no commits.')

    issue_id = args.issue_id

    issues = issue_repository.get_all_issues()
    issue = issues[issue_id]

    file_path = issue.file_path
    start_position = issue.start_position
    end_position = issue.end_position

    print('\nRemoving issue %s from file path %s in branch %s.'
          % (issue_id, file_path, git_repository.active_branch.name))

    with open(file_path, mode='r') as issue_file:
        file_content = issue_file.read()

    file_content_with_issue_removed = file_content[0:start_position] + file_content[end_position:]

    with open(file_path, mode='w') as issue_file:
        issue_file.write(file_content_with_issue_removed)

    git_commit_message = "Closes Issue " + issue_id

    git_repository.index.add([file_path])
    git_repository.index.commit(git_commit_message, skip_hooks=True)
    commit = issue_repository.git_repository.head.commit
    do_commit_contains_duplicate_issue_filepaths_check(issue_repository, commit)

    issue_repository.cache_issue_snapshots_from_unprocessed_commits()

    issues = issue_repository.get_all_issues()
    issue = issues[issue_id]

    print('Done\n')

    page(build_issue_history(issue, issues))
