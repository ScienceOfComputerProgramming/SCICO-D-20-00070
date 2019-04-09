# -*- coding: utf-8 -*-

import os
import stat
import pkg_resources

import threading

from shutil import copyfile
from datetime import datetime

from git import Commit
from gitdb.util import hex_to_bin

from sciit.errors import EmptyRepositoryError, NoCommitsError
from sciit.commit import find_issue_snapshots_in_commit_paths_that_changed
from sciit.functions import write_last_issue_commit_sha, get_last_issue_commit_sha, get_sciit_ignore_path_spec
from sciit.cli.functions import print_progress_bar

from sciit.issue import Issue, IssueSnapshot

from contextlib import closing
import json
import sqlite3

__all__ = ('IssueRepo', )


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class ProgressTracker(object):
    def __init__(self, cli, number_of_commits_for_processing):
        self.cli = cli
        self.number_of_commits_for_processing = number_of_commits_for_processing
        self.commits_scanned = 0
        self.start = datetime.now()

    def processed_commit(self):
        self.commits_scanned += 1
        self._print_commit_progress()

    def _print_commit_progress(self):
        if self.cli:
            duration = datetime.now() - self.start
            commits_scanned = self.commits_scanned
            number_of_commits_for_processing = self.number_of_commits_for_processing

            prefix = 'Processing %d/%d commits: ' % (commits_scanned, number_of_commits_for_processing)
            suffix = ' Duration: %s' % str(duration)

            print_progress_bar(commits_scanned, number_of_commits_for_processing, prefix=prefix, suffix=suffix)


class IssueRepo(object):

    def __init__(self, git_repository):
        self.git_repository = git_repository
        self.issue_dir = self.git_repository.git_dir + '/issues'

        self.issue_snapshot_cache = dict()
        self.commit_branches_cache = dict()

        self.cli = False

    def is_init(self):
        return os.path.exists(self.issue_dir)

    def setup_file_system_resources(self):
        os.makedirs(self.issue_dir)

        open(self.issue_dir + '/HISTORY', 'w').close()
        open(self.issue_dir + '/LAST', 'w').close()

        self._install_hook('post-commit')
        self._install_hook('post-merge')
        self._install_hook('post-checkout')

    def _install_hook(self, hook_name):
        git_hooks_dir = self.git_repository.git_dir + '/hooks/'
        if not os.path.exists(git_hooks_dir):
            os.makedirs(git_hooks_dir)

        source_resource = pkg_resources.resource_filename('sciit.hooks', hook_name)
        destination_path = git_hooks_dir + hook_name
        copyfile(source_resource, destination_path)
        st = os.stat(destination_path)
        os.chmod(destination_path, st.st_mode | stat.S_IEXEC)

    def reset(self):
        def onerror(func, path, excp_info):
            os.chmod(path, stat.S_IWUSR)
            func(path)

        if self.is_init():
            import shutil
            shutil.rmtree(self.issue_dir, onerror=onerror)
        else:
            raise EmptyRepositoryError
    
    def _locally_track_remote_branches(self):
        current_branch = self.git_repository.head.ref.name
        remote_branch_names = [remote.remote_head for remote in self.git_repository.refs if 'remotes/' in remote.path and 'HEAD' not in remote.path]
        head_branch_names = [head.name for head in self.git_repository.heads]
        for branch in remote_branch_names:
            if branch not in head_branch_names:
                self.git_repository.git.execute(['git', 'checkout', branch])
        self.git_repository.git.execute(['git', 'checkout', current_branch])
        
    def cache_issue_snapshots_from_unprocessed_commits(self):

        if not self.git_repository.heads:
            raise NoCommitsError

        # uses git.execute for the check because iter_commits generator cannot correctly identify false or empty list.
        last_issue_commit = get_last_issue_commit_sha(self.issue_dir)
        all_commits = list(self.git_repository.iter_commits('--all'))
        latest_commit = all_commits[0].hexsha

        revision = last_issue_commit + '..' + latest_commit
        str_commits = self.git_repository.git.execute(['git', 'rev-list', '--reverse', revision])

        new_commits = list(self.git_repository.iter_commits(revision)) if str_commits != '' else list()

        # Reprocess head commits in case branch membership has changed.
        head_commits = [head.commit for head in self.git_repository.heads]

        commits_for_processing = new_commits + head_commits

        self._extract_and_synchronise_issue_snapshots_from_commits(commits_for_processing)
        write_last_issue_commit_sha(self.issue_dir, latest_commit)

    def cache_issue_snapshots_from_all_commits(self):

        self._locally_track_remote_branches()

        if not self.git_repository.heads:
            raise NoCommitsError

        # get all commits on all branches, enforcing the topology order of parents to children.
        all_commits = list(self.git_repository.iter_commits(['--all', '--topo-order', '--reverse']))

        if all_commits:
            self._extract_and_synchronise_issue_snapshots_from_commits(all_commits)
            write_last_issue_commit_sha(self.issue_dir, self.git_repository.head.commit.hexsha)
        else:
            raise NoCommitsError

    def _extract_and_synchronise_issue_snapshots_from_commits(self, commits_for_processing):

        ignored_files = get_sciit_ignore_path_spec(self.git_repository)
        progress_tracker = ProgressTracker(self.cli, len(commits_for_processing))

        for commit in commits_for_processing:
            self._cache_issue_snapshots_from_commit(commit, ignored_files, progress_tracker)

    def _cache_issue_snapshots_from_commit(self, commit, ignored_files, progress_tracker):
        changed_issue_snapshots, files_changed_in_commit, in_branches = \
            find_issue_snapshots_in_commit_paths_that_changed(commit, ignore_files=ignored_files)

        unchanged_issue_snapshots = self._find_unchanged_issue_snapshots_in_parents(
            commit, in_branches, files_changed_in_commit)

        all_commit_issue_snapshots = changed_issue_snapshots + unchanged_issue_snapshots
        self._serialize_issue_snapshots_to_db(commit.hexsha, all_commit_issue_snapshots)

        progress_tracker.processed_commit()

    def _find_unchanged_issue_snapshots_in_parents(self, commit, in_branches, files_changed_in_commit):
        result = list()

        for parent_commit in commit.parents:
            parent_issue_snapshots = self.find_issue_snapshots_by_commit(parent_commit.hexsha)
            unchanged_issue_snapshots_in_parent = \
                [parent_snapshot for parent_snapshot in parent_issue_snapshots
                 if parent_snapshot.filepath not in files_changed_in_commit]

            for unchanged_issue_snapshot_in_parent in unchanged_issue_snapshots_in_parent:
                issue_snapshot = IssueSnapshot(commit, unchanged_issue_snapshot_in_parent.data, in_branches)
                result.append(issue_snapshot)

        return result

    def get_all_issues(self, rev=None):
        return self.build_history(rev)

    def get_open_issues(self, rev=None):
        history = self.build_history(rev)
        return {issue_id: issue for issue_id, issue in history.items() if issue.status[0] == 'Open'}

    def build_history(self, revision=None, issue_ids=None):

        if not self.git_repository.heads:
            raise NoCommitsError

        history = dict()

        issue_snapshots = self.find_issue_snapshots(revision)
        head_commits = {head.name: head.commit.hexsha for head in self.git_repository.heads}

        for issue_snapshot in issue_snapshots:

            issue_id = issue_snapshot.issue_id
            if issue_ids is None or issue_id in issue_ids:
                if issue_id not in history:
                    history[issue_id] = Issue(issue_id, history, head_commits)
                history[issue_id].update(issue_snapshot)

        return history

    def find_issue_snapshots(self, revision=None):
        if revision is not None:
            commit_hexshas_str = self.git_repository.git.execute(['git', 'rev-list', '--reverse', revision])
            if commit_hexshas_str != '':
                commit_hexshas = commit_hexshas_str.split('\n')
                return self._deserialize_issue_snapshots_from_db(commit_hexshas)
        else:
            return self._deserialize_issue_snapshots_from_db()

    def find_issue_snapshots_by_commit(self, commit_hexsha):
        if commit_hexsha not in self.issue_snapshot_cache:
            issue_snapshots = self._deserialize_issue_snapshots_from_db([commit_hexsha])
            self.issue_snapshot_cache[commit_hexsha] = issue_snapshots
        return self.issue_snapshot_cache[commit_hexsha]

    def _serialize_issue_snapshots_to_db(self, commit_hexsha, issue_snapshots):
        row_values = [
            (commit_hexsha,
             issue_snapshot.issue_id,
             json.dumps(issue_snapshot.data),
             ','.join(issue_snapshot.in_branches))
            for issue_snapshot in issue_snapshots
        ]

        with closing(sqlite3.connect(self.issue_dir + '/issues.db')) as connection:
            cursor = connection.cursor()
            self._create_issue_snapshot_table(cursor)
            cursor.executemany("INSERT INTO IssueSnapshot VALUES(?, ?, ?, ?)", row_values)
            connection.commit()
        self.issue_snapshot_cache[commit_hexsha] = issue_snapshots

    def _deserialize_issue_snapshots_from_db(self, commit_hexshas=None):
        result = list()

        with closing(sqlite3.connect(self.issue_dir + '/issues.db')) as connection:
            cursor = connection.cursor()
            cursor.row_factory = dict_factory
            self._create_issue_snapshot_table(cursor)
            if commit_hexshas is None:
                row_values = cursor.execute("SELECT * FROM IssueSnapshot").fetchall()
            else:
                question_marks = ','.join(['?'] * len(commit_hexshas))
                row_values = cursor.execute(
                    f"""
                    SELECT * FROM IssueSnapshot WHERE commit_sha in({question_marks})
                    """,
                    commit_hexshas).fetchall()

            for row_value in row_values:
                commit = Commit(self.git_repository, hex_to_bin(row_value['commit_sha']))
                data = json.loads(row_value['json_data'])
                in_branches = row_value['in_branches'].split(',')
                issue_snapshot = IssueSnapshot(commit, data, in_branches)
                result.append(issue_snapshot)

        return result

    @staticmethod
    def _create_issue_snapshot_table(cursor):
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS IssueSnapshot(
             commit_sha TEXT,
             issue_id TEXT,
             json_data BLOB,
             in_branches TEXT,
             UNIQUE (commit_sha, issue_id) ON CONFLICT REPLACE
            )
            """
        )
