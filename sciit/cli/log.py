# -*- coding: utf-8 -*-
"""
Assists with running git sciit log commands, similar to the git log command but shows the open issues for each commit.

    Example:
        This command is accessed via:
        
            $ git sciit log [-h] [revision]
"""

from sciit.cli.color import Color
from sciit.cli.functions import page


def log(args):
    if args.revision:
        revision = args.revision
    else:
        revision = args.repo.head

    args.repo.sync()
    all_issue_commits = list(args.repo.iter_issue_commits(revision))
    output = page_log(all_issue_commits)
    return output


def page_log(issue_commits):
    output = ''
    for issue_commit in issue_commits:
        output += build_log_item(issue_commit)
    page(output)
    return output


def build_log_item(issue_commit):
    time_format = '%a %b %d %H:%M:%S %Y %z'
    date = issue_commit.commit.authored_datetime.strftime(time_format)
    output = Color.bold_yellow(f'commit {issue_commit.hexsha}')
    output += f'\nAuthor:\t {issue_commit.commit.author.name} <{issue_commit.commit.author.email}>'
    output += f'\nDate:\t {date}'
    output += f'\n{Color.bold_red(f"Open Issues: {issue_commit.open_issues}")}'
    output += f'\n'
    output += f'\n{issue_commit.commit.message}'
    output += f'\n'
    return output

