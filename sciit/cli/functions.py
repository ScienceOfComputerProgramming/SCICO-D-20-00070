# -*- coding: utf-8 -*-

import pydoc
import pkg_resources

from sciit.functions import get_sciit_ignore_path_spec
from sciit.commit import find_issue_snapshots_in_commit_paths_that_changed
from sciit.errors import RepoObjectDoesNotExistError
from .color import ColorPrint


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

    issue_snapshots, changed_paths, in_branchesgitgit  = \
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


def print_status_summary(issue_repository):
    try:
        location = issue_repository.git_repository.head.ref.name
    except TypeError:
        location = 'DETACHED:' + issue_repository.git_repository.head.commit.hexsha

    try:
        issues = issue_repository.get_open_issues()
        # show issue status at head to the user
        if len(issues) > 0:
            result = str(len(issues)) + ' Open Issues @' + location
            ColorPrint.bold_red(result)
        else:
            result = 'No Open Issues @' + location
            ColorPrint.bold_green(result)

    except RepoObjectDoesNotExistError as error:
        ColorPrint.bold_red(error)
        print('Solve error by rebuilding issue repository using: git sciit init -r')
        exit(127)
