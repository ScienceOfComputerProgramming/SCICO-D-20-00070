from sciit.functions import get_sciit_ignore_path_spec
from sciit.read_commit import find_issue_snapshots_in_commit_paths_that_changed
from sciit.cli.color import ColorPrint


def do_commit_contains_duplicate_issue_file_paths_check(issue_repository, commit):

    git_repository = issue_repository.git_repository

    ignored_files = get_sciit_ignore_path_spec(issue_repository.git_repository)

    issue_snapshots, _, _ = \
        find_issue_snapshots_in_commit_paths_that_changed(commit, ignore_files=ignored_files)

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

    def __init__(self, issue_repository, target_branch, message, push=True):

        self._issue_repository = issue_repository
        self._target_branch = target_branch
        self._commit_message = message

        self._push = push

        self._starting_branch_name = self._git_repository.active_branch.name

        self.file_paths = list()

    @property
    def _git_repository(self):
        return self._issue_repository.git_repository

    def __enter__(self):
        self._git_repository.create_head(self._target_branch)
        self._git_repository.git.checkout(self._target_branch)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._git_repository.index.add(self.file_paths)
        commit = self._git_repository.index.commit(self._commit_message, skip_hooks=True)

        do_commit_contains_duplicate_issue_file_paths_check(self._issue_repository, commit)

        self._issue_repository.cache_issue_snapshots_from_unprocessed_commits()

        if self._push:
            try:
                self._git_repository.git.push('origin', self._target_branch)
            except ValueError:
                pass

        for file_path in self.file_paths:
            self._git_repository.git.checkout(file_path)
        self._git_repository.git.checkout(self._starting_branch_name)
