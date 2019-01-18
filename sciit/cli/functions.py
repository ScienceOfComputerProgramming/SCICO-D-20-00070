# -*- coding: utf-8 -*-

import pydoc
import pkg_resources

from sciit.functions import get_sciit_ignore_path_spec
from sciit.commit import find_issue_snapshots_in_commit_paths_that_changed
from sciit.errors import RepoObjectDoesNotExistError
from .color import ColorPrint, ColorText


def page(output):
    pydoc.pipepager(output, cmd='less -FRSX')


def yes_no_option(msg=''):
    option = input(msg + ' [y/N]: ')
    if option is 'Y' or option is 'y':
        return True
    else:
        return False


def read_sciit_version():
    filename = pkg_resources.resource_filename('sciit.man', 'VERSION')
    with open(filename, 'rb') as f:
        return f.read().decode('utf-8')


def do_repository_is_init_check(issue_repository):
    if not issue_repository.is_init():
        ColorPrint.bold_red('Error: Issue repository not setup.')
        print('Solve this error by building issue repository using: git sciit init')
        exit(127)


def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=50, fill='#'):
    """
    From https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console

    Args:
       :(int) iteration: current iteration
       :(int) total: total iterations
       :(str) prefix: prefix string
       :(str) suffix: suffix string
       :(str) decimals: positive number of decimals in percent complete
       :(int) length: character length of bar
       :(str) fill: bar fill character
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end='\r')

    if iteration == total:
        print()


def do_commit_contains_duplicate_issue_filepaths_check(issue_repository, commit):

    git_repository = issue_repository.git_repository

    ignored_files = get_sciit_ignore_path_spec(issue_repository.git_repository)

    issue_snapshots, changed_paths, _ = \
        find_issue_snapshots_in_commit_paths_that_changed(commit, ignore_files=ignored_files)

    if len(set(issue_snapshots)) != len(issue_snapshots):
        file_paths_by_issue_id = dict()

        for issue_snapshot in issue_snapshots:
            issue_id = issue_snapshot.issue_id
            if issue_id not in file_paths_by_issue_id:
                file_paths_by_issue_id[issue_id] = list()
            file_paths_by_issue_id[issue_id].append(issue_snapshot.filepath)

        duplicates =\
            {issue_id: file_paths for issue_id, file_paths in file_paths_by_issue_id.items() if len(file_paths) > 1}

        for (issue_id, file_paths) in duplicates.items():
            ColorPrint.bold_red(f'Duplicate Issue: {issue_id}')
            for file_found in file_paths:
                ColorPrint.red(f'\tfound in {file_found}')

        git_repository.git.execute(['git', 'reset', 'HEAD~1', '--soft'])
        ColorPrint.bold_red(f'HEAD @: {git_repository.head.commit.summary} ~ {git_repository.head.commit.hexsha[:7]}')
        exit()


def make_status_summary_string(all_issues):
    open = sum(issue.status[0] == 'Open' for issue in all_issues.values())
    closed_str = str(len(all_issues) - open)
    open_str = str(open)

    padding = max(len(closed_str), len(open_str))

    output = ''
    output += ColorText.bold_red(f'Open Issues:   ' + str(open_str.rjust(padding)))
    output += '\n'
    output += ColorText.bold_green(f'Closed Issues: ' + str(closed_str.rjust(padding)))
    output += '\n\n'

    return output


def build_status_summary(issue_repository, revision=None):

    try:
        all_issues = issue_repository.get_all_issues(revision)
        return make_status_summary_string(all_issues)

    except RepoObjectDoesNotExistError as error:
        ColorPrint.bold_red(error)
        print('Solve error by rebuilding issue repository using: git sciit init -r')
        exit(127)


def build_status_table(issue_repository, revision=None):

    all_issues = issue_repository.get_all_issues(revision)
    output = make_status_summary_string(all_issues)

    title_width = 50
    all_issues = list(all_issues.values())
    all_issues.sort(key= lambda issue: issue.last_authored_date, reverse=True)

    for issue in all_issues:
        issue_title = issue.title

        if len(issue_title) > title_width - 3:
            output += ColorText.bold_yellow(issue_title[0:title_width-5] + '...: ')
        else:
            output += ColorText.bold_yellow((issue_title + ': ').ljust(title_width))

        if issue.status[0] is 'Closed':
            issue_status = ColorText.bold_green(issue.status[0].ljust(6))
        else:
            issue_status = ColorText.bold_red(issue.status[0].ljust(6))

        output += issue_status
        output += "\nid: " + issue.issue_id.ljust(title_width + 4) + '\n\n'

    output += '\n'

    return output


def subheader(header):
    return ColorText.bold(f'\n{header}')


def build_issue_history(issue_item, view=None):
    """
    Builds a string representation of a issue history item for showing to the terminal with ANSI color codes

    Args:
        :(dict) item: item to build string from

    Returns:
        :(str): string representation of issue history item
    """
    status, sub_status = issue_item.status
    status_str = f'{status} ({sub_status})'

    participants = ', '.join(issue_item.participants)

    output = ''
    output += f'\nTitle:             ' + ColorText.bold_yellow(f"{issue_item.title}")
    output += f'\nID:                {issue_item.issue_id}'
    output += f'\nStatus:            ' + (ColorText.green(status_str) if status == 'Closed' else ColorText.red(status_str))
    output += f'\n'
    output += f'\nClosed:            {issue_item.closer} | {issue_item.closed_date}' if issue_item.closer else ''
    output += f'\nLast Change:       {issue_item.last_author} | {issue_item.last_authored_date_string}'
    output += f'\nCreated:           {issue_item.creator} | {issue_item.created_date_string}'
    output += f'\n'
    output += f'\nAssigned To:       {issue_item.assignees}' if issue_item.assignees else ''

    output += f'\nParticipants:      {participants}'
    output += f'\nDue Date:          {issue_item.due_date}' if issue_item.due_date else ''
    output += f'\nLabels:            {issue_item.label}' if issue_item.label else ''
    output += f'\nWeight:            {issue_item.weight}' if issue_item.weight else ''
    output += f'\nPriority:          {issue_item.priority}' if issue_item.priority else ''

    blocker_issues = issue_item.blockers

    if len(blocker_issues) > 0:
        blockers_status = list()

        for blocker_issue_id, blocker_issue in blocker_issues.items():
            blocker_status = blocker_issue.status[0] if blocker_issue is not None else '?'
            blockers_status.append('%s(%s)' % (blocker_issue_id,blocker_status))

        blockers_str = '\n                   '.join(blockers_status)
        output += f'\nBlockers:          {blockers_str}'

    output += f'\nSize:              {str(issue_item.size)}' if issue_item.size else ''
    output += f'\nLatest file path:  {issue_item.file_path}' if len(issue_item.file_paths) > 0 else ''

    if (view == 'full') and len(issue_item.file_paths) > 0:
        output += "\nBranch file paths:"
        first_line = True
        for branch, path in issue_item.file_paths.items():
            if first_line:
                first_line = False
                padding = " "
            else:
                padding = "                   "
            branch_status = 'open' if branch in issue_item.open_in_branches else 'closed'
            output += f'{padding}{path} @{branch} ({branch_status})\n'

    if issue_item.description:
        output += f'\n\nDescription:'
        output += '\n' if not issue_item.description.startswith('\n') else ''
        output += issue_item.description

    if view == 'full':
        num_revisions = str(len(issue_item.revisions))
        output += subheader(f'\nRevisions to Issue ({num_revisions}):\n')

        for revision in issue_item.revisions:

            changes = revision['changes']
            output += f'\nIn {revision["commitsha"]} ({len(changes)} items changed):\n'

            for changed_property, new_value in changes.items():
                output += f' {changed_property}: {new_value}\n'

            output += f'\n'
            output += f'{ColorText.bold_yellow("--> made by: " + revision["author"])} - {revision["date"]}\n'
            output += f'    {revision["summary"]}\n'

    if view == 'full':
        num_commits = str(len(issue_item.activity))
        output += subheader(f'\nPresent in Commits ({num_commits}):')
        for commit in reversed(issue_item.activity):
            output += f'\n{commit["date"]} | {commit["commitsha"]} | {commit["author"]} | {commit["summary"]}'

    output += f'\n{ColorText.yellow("*"*90)}\n'

    return output


