import slugify
import os
from sciit.cli.functions import do_commit_contains_duplicate_issue_filepaths_check, build_issue_history, page


def read_input_with_default(prompt, default):

    result = input("%s [%s]:" % (prompt, default)).rstrip('\r\n')

    return result if result != "" else default


def new_issue(args):

    issue_title = input("Enter a title for the issue: ").rstrip()

    issue_id = slugify.slugify(issue_title)
    issue_id = read_input_with_default("Enter the issue id", issue_id)

    file_path = 'backlog/' + issue_id +".md"
    file_path = read_input_with_default("Enter a file path", file_path)

    issue_description = read_input_with_default("Enter a description", "")

    git_commit_message = read_input_with_default("Enter a commit message", "Creates Issue "+issue_title)

    issue_repository = args.repo
    git_repository = issue_repository.git_repository

    starting_branch_name = git_repository.active_branch.name

    git_repository.create_head(issue_id)
    git_repository.git.checkout(issue_id)

    backlog_directory = os.path.dirname(file_path)

    os.makedirs(backlog_directory, exist_ok=True)

    with open(file_path, mode='w') as issue_file:
        issue_file.write(
            f'---\n@issue {issue_id}\n@title {issue_title}\n@description\n{issue_description}\n---\n'
        )

    git_repository.index.add([file_path])
    git_repository.index.commit(git_commit_message, skip_hooks=True)
    commit = issue_repository.git_repository.head.commit
    do_commit_contains_duplicate_issue_filepaths_check(issue_repository, commit)

    issue_repository.cache_issue_snapshots_from_unprocessed_commits()

    git_repository.git.checkout(file_path)
    git_repository.git.checkout(starting_branch_name)

    issues = issue_repository.get_all_issues()
    issue = issues[issue_id]

    page(build_issue_history(issue, issues))