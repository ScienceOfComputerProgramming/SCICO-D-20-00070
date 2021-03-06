# -*- coding: utf-8 -*-

from sciit.cli.styling import Styling
from sciit.cli.functions import page


def log(args):
    revision = args.revision if args.revision else None

    all_issue_commits = args.repo.find_issue_snapshots(revision)
    output = page_log(all_issue_commits)
    return output


def page_log(issue_snapshots):

    commits_and_issue_snapshots = dict()
    for issue_snapshot in reversed(issue_snapshots):
        if issue_snapshot.commit not in commits_and_issue_snapshots:
            commits_and_issue_snapshots[issue_snapshot.commit] = list()
        commits_and_issue_snapshots[issue_snapshot.commit].append(issue_snapshot)

    output = ''
    for commit, issue_snapshot_list in commits_and_issue_snapshots.items():
        output += build_log_item(commit, issue_snapshot_list)
    page(output)
    return output


def build_log_item(commit, issue_snapshot_list):

    issue_snapshot_ids = [issue_snapshot.issue_id for issue_snapshot in issue_snapshot_list]
    issue_snapshot_ids_str = '\n '.join(issue_snapshot_ids)

    time_format = '%a %b %d %H:%M:%S %Y %z'
    date = commit.authored_datetime.strftime(time_format)
    output = Styling.item_title(f'commit {commit.hexsha}')
    output += f'\nAuthor:\t {commit.author.name} <{commit.author.email}>'
    output += f'\nDate:\t {date}'
    output += f'\nOpen Issue Ids:\n {issue_snapshot_ids_str}'
    output += f'\n'
    output += f'\n{commit.message}'
    output += f'\n'
    return output
