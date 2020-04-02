import os
import slugify
from sciit.cli.functions import do_repository_has_no_commits_warning, build_issue_history, page


def read_input_with_default(prompt, default):

    result = input("%s [%s]:" % (prompt, default)).rstrip('\r\n')

    return result if result != "" else default


def new_issue(args):

    issue_repository = args.repo
    git_repository = issue_repository.git_repository

    if not git_repository.heads:
        do_repository_has_no_commits_warning()
        return

    issue_title = input("Enter a title for the issue: ").rstrip()

    issue_id = slugify.slugify(issue_title)
    issue_id = read_input_with_default("Enter the issue id", issue_id)

    file_path = 'backlog/' + issue_id + ".md"
    file_path = read_input_with_default("Enter a file path", file_path)

    issue_description = read_input_with_default("Enter a description", "")

    git_commit_message = read_input_with_default("Enter a commit message", "Creates Issue " + issue_id)

    with WithGitCommitToIssue(issue_repository, issue_id, git_commit_message) as commit_to_issue:

        backlog_directory = os.path.dirname(file_path)
        os.makedirs(backlog_directory, exist_ok=True)

        with open(file_path, mode='w') as issue_file:
            issue_file.write(
                f'---\n@issue {issue_id}\n@title {issue_title}\n@description\n{issue_description}\n---\n'
            )

        commit_to_issue.file_paths.append(file_path)

    if args.accept:
        print("Performing merge to master to accept issue...")
        git_repository.git.merge(issue_id)
        print("Done. Remember to push changes to origin.")

    issues = issue_repository.get_all_issues()
    issue = issues[issue_id]

    page(build_issue_history(issue, issues))



