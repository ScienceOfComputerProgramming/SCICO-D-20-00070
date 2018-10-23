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
        revision = args.repo.git_repository.head

    args.repo.cache_issue_snapshots_from_unprocessed_commits()
    all_issue_commits = args.repo.find_issue_snapshots_by_revision(revision)
    output = page_log(all_issue_commits)
    return output


def page_log(commits_and_issue_snapshots):
    output = ''
    for commit, issue_snapshot_list in commits_and_issue_snapshots.items():
        output += build_log_item(commit, issue_snapshot_list)
    page(output)
    return output


def build_log_item(commit, issue_snapshot_list):
    time_format = '%a %b %d %H:%M:%S %Y %z'
    date = commit.authored_datetime.strftime(time_format)
    output = Color.bold_yellow(f'commit {commit.hexsha}')
    output += f'\nAuthor:\t {commit.author.name} <{commit.author.email}>'
    output += f'\nDate:\t {date}'
    output += f'\n{Color.bold_red(f"Open Issues: {len(issue_snapshot_list)}")}'
    output += f'\n'
    output += f'\n{commit.message}'
    output += f'\n'
    return output

