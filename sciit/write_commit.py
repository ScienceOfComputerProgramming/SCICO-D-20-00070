import os
import logging
import slugify

from sciit.functions import get_sciit_ignore_path_spec
from sciit.read_commit import find_issue_snapshots_in_commit_paths_that_changed
from sciit.cli.color import ColorPrint


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


class GitCommitToIssue:

    def __init__(self, issue_repository, target_branch, message, push=True, origin_url=None):

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
        if self._target_branch not in self._git_repository.heads:
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


def create_new_issue(issue_repository, title, description='', commit_message=None, issue_id=None, file_path=None):

    _issue_id = slugify.slugify(title) if issue_id is None else issue_id
    _commit_message = "Creates Issue %s." % _issue_id if commit_message is None else commit_message

    working_dir = issue_repository.git_repository.working_dir

    _file_path = f"{working_dir}{os.sep}backlog{os.sep}{_issue_id}.md" if file_path is None else file_path

    with GitCommitToIssue(issue_repository, _issue_id, _commit_message) as commit_to_issue:

        backlog_directory = os.path.dirname(_file_path)
        os.makedirs(backlog_directory, exist_ok=True)

        with open(_file_path, mode='w') as issue_file:
            issue_file.write(
                f'---\n@issue {_issue_id}\n@title {title}\n@description\n{description}\n---\n'
            )

        commit_to_issue.file_paths.append(_file_path)
        return _issue_id

