import slugify

from sciit.cli.functions import do_repository_has_no_commits_warning, build_issue_history, page

from sciit.write_commit import create_issue


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

    create_issue(issue_repository, issue_title, issue_description, git_commit_message, issue_id, file_path)

    if args.accept:
        print("Performing merge to master to accept issue...")
        git_repository.git.merge(issue_id)
        print("Done. Remember to push changes to origin.")

    issues = issue_repository.get_all_issues()
    issue = issues[issue_id]

    page(build_issue_history(issue, issues))
