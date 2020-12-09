# -*- coding: utf-8 -*-

import pydoc
import pkg_resources

from sciit.errors import RepoObjectDoesNotExistError
from .styling import Styling


def page(output):
    pydoc.pipepager(output, cmd='less -FRSX')


def yes_no_option(msg=''):
    option = input(msg + ' [y/N]: ')
    return option in {'Y', 'y'}


def read_sciit_version():
    filename = pkg_resources.resource_filename('sciit.man', 'VERSION')
    with open(filename, 'rb') as version_file_handle:
        return version_file_handle.read().decode('utf-8')


def do_repository_is_init_check_and_exit_if_not(issue_repository):
    if not issue_repository.is_init():
        print(Styling.error_warning('git sciit error fatal: issue repository not initialized.'))
        print(Styling.error_warning('Solve this error by (re)building the issue repository using: git sciit init [-r]'))
        exit(127)


def do_invalid_git_repository_warning_and_exit():
    print(Styling.error_warning('fatal: not a git repository (or any parent up to mount point /)'))
    print(Styling.error_warning('Stopping at filesystem boundary(GIT_DISCOVERY_ACROSS_FILESYSTEM not set).'))
    exit(127)


def do_repository_has_no_commits_warning_and_exit():
    print(' ')
    print(Styling.error_warning('git sciit error fatal: the repository has no commits.'))
    print(Styling.error_warning('Create an initial commit before creating a new issue'))
    exit(127)


def do_git_command_warning_and_exit(command):
    print(Styling.error_warning(f'git sciit error fatal: bad git command executed within sciit {str(command)}'))
    exit(127)


def make_status_summary_string(all_issues):
    open_issues_count = sum(issue.status[0] == 'Open' for issue in all_issues.values())
    closed_str = str(len(all_issues) - open_issues_count)
    open_str = str(open_issues_count)

    padding = max(len(closed_str), len(open_str))

    output = ''
    output += Styling.open_status(f'Open Issues:   ' + str(open_str.rjust(padding)))
    output += '\n'
    output += Styling.closed_status(f'Closed Issues: ' + str(closed_str.rjust(padding)))
    output += '\n\n'

    return output


def build_status_summary(issue_repository, revision=None):

    try:
        all_issues = issue_repository.get_all_issues(revision)
        return make_status_summary_string(all_issues)

    except RepoObjectDoesNotExistError as error:
        print(Styling.error_warning(error))
        print(Styling.error_warning('Solve this error by (re)building issue repository using: git sciit init [-r].'))
        exit(127)


def _title_as_key(issue): return issue.title if issue.title is not None else ''


def build_status_table(issue_repository, revision=None):

    all_issues = issue_repository.get_all_issues(revision)
    output = make_status_summary_string(all_issues)

    title_width = 120
    all_issues = list(all_issues.values())
    all_issues.sort(key=_title_as_key)

    for issue in all_issues:
        issue_title = issue.title if issue.title is not None else ''

        if len(issue_title) > title_width - 3:
            output += Styling.item_title(issue_title[0:title_width - 5] + '...: ')
        else:
            output += (Styling.item_title(issue_title) + ': ').ljust(title_width)

        if issue.status[0] == 'Closed':
            issue_status = Styling.closed_status(issue.status[0].ljust(6))
        else:
            issue_status = Styling.open_status(issue.status[0].ljust(6))

        output += issue_status
        output += "\nid: " + issue.issue_id.ljust(title_width + 4) + '\n\n'

    output += '\n'

    return output


def subheading(header):
    return Styling.item_subtitle(f'\n{header}')


def build_issue_history(issue_item, view=None):
    """
    Builds a string representation of a issue history item for showing to the terminal with ANSI color codes

    Args:
        :(dict) item: item to build string from

    Returns:
        :(str): string representation of issue history item
    """

    title_str = Styling.item_title(f"{issue_item.title}")

    status, sub_status = issue_item.status
    status_str = f'{status} ({sub_status})'
    status_str_colored = Styling.closed_status(status_str) if status == 'Closed' else Styling.open_status(status_str)

    participants = ', '.join(issue_item.participants)

    output = ''
    output += f'\nTitle:             {title_str}'
    output += f'\nID:                {issue_item.issue_id}'
    output += f'\nStatus:            {status_str_colored}'
    output += f'\nDuration:          {issue_item.duration}' if issue_item.duration else ''

    output += f'\n'

    output += f'\nClosed:            {issue_item.closer} | {issue_item.closed_date}' if issue_item.closer else ''
    output += f'\nLast Change:       {issue_item.last_author} | {issue_item.last_authored_date_string}'
    output += f'\nBegun:             {issue_item.initiator} | {issue_item.work_begun_date}' if issue_item.initiator else ''
    output += f'\nCreated:           {issue_item.creator} | {issue_item.created_date_string}'
    output += f'\n'
    output += f'\nAssigned To:       {issue_item.assignees}' if issue_item.assignees else ''

    output += f'\nParticipants:      {participants}'
    output += f'\nDue Date:          {issue_item.due_date}' if issue_item.due_date else ''
    output += f'\nLabels:            {issue_item.labels}' if issue_item.labels else ''
    output += f'\nWeight:            {issue_item.weight}' if issue_item.weight else ''
    output += f'\nPriority:          {issue_item.priority}' if issue_item.priority else ''

    blocker_issues = issue_item.blockers

    if len(blocker_issues) > 0:
        blockers_status = list()

        for blocker_issue_id, blocker_issue in blocker_issues.items():
            blocker_status = blocker_issue.status[0] if blocker_issue is not None else '?'
            blockers_status.append('%s(%s)' % (blocker_issue_id, blocker_status))

        blockers_str = '\n                   '.join(blockers_status)
        output += f'\nBlockers:          {blockers_str}\n'

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
        output += subheading(f'\nRevisions to Issue ({num_revisions}):\n')

        for revision in issue_item.revisions:

            changes = revision['changes']
            output += f'\nIn {revision["hexsha"]} ({len(changes)} items changed):\n'

            for changed_property, new_value in changes.items():
                output += f' {changed_property}: {new_value}\n'

            output += f'\n'
            output += f'{"--> made by: " + revision["author"]} - {revision["date"]}\n'
            output += f'    {revision["summary"]}\n'

    if view == 'full':
        num_commits = str(len(issue_item.activity))
        output += subheading(f'\nPresent in Commits ({num_commits}):')
        for commit in reversed(issue_item.activity):
            output += f'\n{commit["date"]} | {commit["hexsha"]} | {commit["author"]} | {commit["summary"]}'

    output += f'\n\n{Styling.item_subtitle("*"*90)}\n'

    return output
