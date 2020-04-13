import os
import logging
import re
import slugify

from sciit.functions import get_sciit_ignore_path_spec
from sciit.read_commit import find_issue_snapshots_in_commit_paths_that_changed
from sciit.cli.color import ColorPrint

from sciit.regex import get_file_object_pattern, IssuePropertyRegularExpressions, add_comment_chars, \
    strip_comment_chars, get_issue_property_regex


def do_commit_contains_duplicate_issue_file_paths_check(issue_repository, commit):

    git_repository = issue_repository.git_repository

    ignored_files = get_sciit_ignore_path_spec(issue_repository.git_repository)

    issue_snapshots, _, _ = \
        find_issue_snapshots_in_commit_paths_that_changed(
            commit, git_working_dir=git_repository.working_dir, ignore_files=ignored_files)

    if len(set(issue_snapshots)) != len(issue_snapshots):
        file_paths_by_issue_id = dict()

        for issue_snapshot in issue_snapshots:
            issue_id = issue_snapshot.issue_id
            if issue_id not in file_paths_by_issue_id:
                file_paths_by_issue_id[issue_id] = list()
            file_paths_by_issue_id[issue_id].append(issue_snapshot.file_path)

        duplicates =\
            {issue_id: file_paths for issue_id, file_paths in file_paths_by_issue_id.items() if len(file_paths) > 1}

        for (issue_id, file_paths) in duplicates.items():
            ColorPrint.bold_red(f'Duplicate Issue: {issue_id}')
            for file_found in file_paths:
                ColorPrint.red(f'\tfound in {file_found}')

        git_repository.git.execute(['git', 'reset', 'HEAD~1', '--soft'])
        ColorPrint.bold_red(f'HEAD @: {git_repository.head.commit.summary} ~ {git_repository.head.commit.hexsha[:7]}')
        exit()


class _GitCommitToIssue:

    def __init__(self, issue_repository, target_branch, message, push, origin_url):

        self._issue_repository = issue_repository
        self._target_branch = target_branch
        self._commit_message = message

        self._origin_url = origin_url

        self._push = push

        self._starting_branch_name = self._git_repository.active_branch.name

        self.file_paths = list()

    @property
    def _git_repository(self):
        return self._issue_repository.git_repository

    def __enter__(self):

        head_branch_names = [head.name for head in self._git_repository.heads]

        if self._target_branch not in head_branch_names:
            self._git_repository.create_head(self._target_branch)
        self._git_repository.git.checkout(self._target_branch)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._git_repository.index.add(self.file_paths)
        commit = self._git_repository.index.commit(self._commit_message, skip_hooks=True)

        do_commit_contains_duplicate_issue_file_paths_check(self._issue_repository, commit)

        self._issue_repository.cache_issue_snapshots_from_unprocessed_commits()

        if self._push:
            try:
                origin = self._git_repository.remote('origin')
                if origin is None:
                    if self._origin_url is None:
                        raise ValueError()
                    else:
                        origin = self._git_repository.create_remote('origin', self._origin_url)

                self._git_repository.git.push("--set-upstream", origin, self._git_repository.head.ref)
            except ValueError:
                logging.warning("Couldn't push to branch [%s]." % self._target_branch)

        for file_path in self.file_paths:
            self._git_repository.git.checkout(file_path)

        self._git_repository.git.checkout(self._starting_branch_name)


def git_commit_to_issue(issue_repository, target_branch, git_commit_message, push=True, origin_url=None):
    return _GitCommitToIssue(issue_repository, target_branch, git_commit_message, push, origin_url)


def create_issue(issue_repository, title, description='', git_commit_message=None, issue_id=None, file_path=None):

    _issue_id = slugify.slugify(title) if issue_id is None else issue_id
    _commit_message = "Creates Issue %s." % _issue_id if git_commit_message is None else git_commit_message

    working_dir = issue_repository.git_repository.working_dir

    _file_path = f"{working_dir}{os.sep}backlog{os.sep}{_issue_id}.md" if file_path is None else file_path

    with git_commit_to_issue(issue_repository, _issue_id, _commit_message) as commit_to_issue:

        backlog_directory = os.path.dirname(_file_path)
        os.makedirs(backlog_directory, exist_ok=True)

        with open(_file_path, mode='w') as issue_file:
            issue_file.write(
                f'---\n@issue {_issue_id}\n@title {title}\n@description\n{description}\n---\n'
            )

        commit_to_issue.file_paths.append(_file_path)
        return _issue_id


def close_issue(issue_repository, issue, branch_names=None):

    _branch_names = branch_names if branch_names is not None else issue.latest_snapshots_in_open_branches

    for branch_name, issue_snapshot in _branch_names:

        git_commit_message = "Closes issue [%s] in branch [%s]." %(issue.issue_id, branch_name)

        with git_commit_to_issue(issue_repository, branch_name, git_commit_message) as commit_to_issue:

            file_path = issue.file_path
            start_position = issue.start_position
            end_position = issue.end_position

            with open(file_path, mode='r') as issue_file:
                file_content = issue_file.read()

            file_content_with_issue_removed = file_content[0:start_position] + file_content[end_position:]

            with open(file_path, mode='w') as issue_file:
                issue_file.write(file_content_with_issue_removed)

            commit_to_issue.file_paths.append(issue.file_path)


def update_issue(issue_repository, issue, changes, message=None):

    latest_branch = issue.newest_issue_snapshot.in_branches[0]

    _message = message if message is not None else "Updates Issue %s." % issue.issue_id

    with git_commit_to_issue(issue_repository, latest_branch, _message) as commit_to_issue:

        new_sciit_issue_file_content = _get_changed_file_content(issue, changes)

        with open(issue.working_file_path, 'w') as sciit_issue_file:
            sciit_issue_file.write(new_sciit_issue_file_content)

        commit_to_issue.file_paths.append(issue.file_path)


def _get_changed_file_content(sciit_issue, changes):

    comment_pattern = get_file_object_pattern(sciit_issue.file_path)

    with open(sciit_issue.working_file_path, 'r') as sciit_issue_file:

        file_content = sciit_issue_file.read()
        sciit_issue_content_in_file = file_content[sciit_issue.start_position:sciit_issue.end_position]

    sciit_issue_content, indent = strip_comment_chars(comment_pattern, sciit_issue_content_in_file)

    for key in ['title', 'due_date', 'weight', 'labels']:
        if key in changes:
            sciit_issue_content = _update_single_line_property_in_file_content(
                    get_issue_property_regex(key), sciit_issue_content, key, changes[key])

    if 'description' in changes and not (changes['description'] == '' and sciit_issue.description is None):
        sciit_issue_content = _update_description_in_file_content(sciit_issue_content, changes['description'])

    sciit_issue_content = add_comment_chars(comment_pattern, sciit_issue_content, indent)

    return \
        file_content[0:sciit_issue.start_position] + \
        sciit_issue_content + \
        file_content[sciit_issue.end_position:]


def _update_single_line_property_in_file_content( pattern, file_content, label, new_value):

    old_match = re.search(pattern, file_content)
    if old_match:
        old_start, old_end = old_match.span(1)
        return file_content[0:old_start] + str(new_value) + file_content[old_end:]
    else:
        return file_content + f'\n@{label} {new_value}'


def _update_description_in_file_content(file_content, new_value):

    old_match = re.search(IssuePropertyRegularExpressions.DESCRIPTION, file_content)
    if old_match:
        old_start, old_end = old_match.span(1)
        return file_content[0:old_start] + '\n' + new_value + file_content[old_end:]
    else:
        return file_content + f'\n@description\n{new_value}'

