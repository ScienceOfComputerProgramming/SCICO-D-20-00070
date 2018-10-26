# -*- coding: utf-8 -*-

import os
import stat
import pkg_resources

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
        print(new_commits)
        # Reprocess head commits in case branch membership has changed.
        head_commits = [head.commit for head in self.git_repository.heads]

        commits_for_processing = new_commits + head_commits

        self._extract_and_synchronise_issue_snapshots_from_commits(commits_for_processing)
        write_last_issue_commit_sha(self.issue_dir, latest_commit)

    def cache_issue_snapshots_from_all_commits(self):
        if len(self.git_repository.heads) < 1:
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

        commits_scanned = 0
        start = datetime.now()

        for commit in commits_for_processing:
            commits_scanned += 1
            self._print_commit_progress(datetime.now(), start, commits_scanned, len(commits_for_processing))

            changed_issue_snapshots, files_changed_in_commit = \
                find_issue_snapshots_in_commit_paths_that_changed(commit, ignore_files=ignored_files)

            unchanged_issue_snapshots = self._find_unchanged_issue_snapshots_in_parents(
                commit, files_changed_in_commit)

            all_commit_issue_snapshots = changed_issue_snapshots + unchanged_issue_snapshots
            self._serialize_issue_snapshots_to_db(commit.hexsha, all_commit_issue_snapshots)

    def _find_unchanged_issue_snapshots_in_parents(self, commit, files_changed_in_commit):

        result = list()

        for parent_commit in commit.parents:

            parent_issue_snapshots = self.find_issue_snapshots_by_commit(parent_commit.hexsha)

            unchanged_issue_snapshots_in_parent = \
                [parent_snapshot for parent_snapshot in parent_issue_snapshots
                 if parent_snapshot.filepath not in files_changed_in_commit]

            for unchanged_issue_snapshot_in_parent in unchanged_issue_snapshots_in_parent:
                result.append(
                    IssueSnapshot(
                        parent_commit,
                        unchanged_issue_snapshot_in_parent.data,
                        unchanged_issue_snapshot_in_parent.in_branches))

        return result

    def _print_commit_progress(self, now, start, current, total):
        if self.cli:
            duration = now - start
            prefix = 'Processing %d/%d commits: ' % (current, total)
            suffix = ' Duration: %s' % str(duration)

            print_progress_bar(current, total, prefix=prefix, suffix=suffix)

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
            issue_snapshots = self._deserialize_issue_snapshots_from_db(commit_hexsha)
            self.issue_snapshot_cache[commit_hexsha] = issue_snapshots
        return self.issue_snapshot_cache[commit_hexsha]

    def _serialize_issue_snapshots_to_db(self, commit_hexsha, issue_snapshots):
        row_values = [
            (commit_hexsha, issue.issue_id, json.dumps(issue.data), ','.join(issue.in_branches))
            for issue in issue_snapshots]

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
