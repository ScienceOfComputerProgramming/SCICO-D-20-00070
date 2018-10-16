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

        last_issue_commit = get_last_issue_commit_sha(self.issue_dir)
        commits = list(self.git_repository.iter_commits('--all'))

        latest_commit = commits[0].hexsha
        revision = last_issue_commit + '..' + latest_commit

        # uses git.execute for the check because iter_commits generator cannot correctly identify false or empty list.
        str_commits = self.git_repository.git.execute(['git', 'rev-list', revision])

        if str_commits != '':
            commits = list(self.git_repository.iter_commits(revision))
            self._extract_and_synchronise_issue_snapshots_from_commits(commits, len(commits))
            write_last_issue_commit_sha(self.issue_dir, latest_commit)

    def cache_issue_snapshots_from_all_commits(self):
        if len(self.git_repository.heads) < 1:
            raise NoCommitsError

        # get all commits on all branches, enforcing the topology order of parents to children.
        all_commits = self.git_repository.iter_commits(['--all', '--topo-order', '--reverse'])
        num_commits = int(self.git_repository.git.execute(['git', 'rev-list', '--all', '--count']))

        if all_commits:
            self._extract_and_synchronise_issue_snapshots_from_commits(all_commits, num_commits)
            write_last_issue_commit_sha(self.issue_dir, self.git_repository.head.commit.hexsha)
        else:
            raise NoCommitsError

    def _extract_and_synchronise_issue_snapshots_from_commits(self, all_commits, num_commits):

        ignored_files = get_sciit_ignore_path_spec(self.git_repository)

        commits_scanned = 0
        start = datetime.now()

        changed_commit_issue_snapshots = dict()

        for commit in all_commits:
            commits_scanned += 1
            self.print_commit_progress(datetime.now(), start, commits_scanned, num_commits)

            changed_issue_snapshots, files_changed_in_commit = \
                find_issue_snapshots_in_commit_paths_that_changed(commit, ignore_files=ignored_files)
            changed_commit_issue_snapshots[commit] = changed_issue_snapshots

            unchanged_issue_snapshots = list()

            for parent in commit.parents:
                parent_commit = parent
                if parent_commit in changed_commit_issue_snapshots:
                    parent_issue_snapshots = changed_commit_issue_snapshots[parent_commit]
                    unchanged_issue_snapshots_in_parent = \
                        [parent_snapshot for parent_snapshot in parent_issue_snapshots
                         if parent_snapshot.filepath not in files_changed_in_commit]
                    unchanged_issue_snapshots.extend(unchanged_issue_snapshots_in_parent)
            all_issue_snapshots = changed_issue_snapshots + unchanged_issue_snapshots
            self._serialize_issue_snapshots_to_db(commit.hexsha, all_issue_snapshots)

    def print_commit_progress(self, now, start, current, total):
        if self.cli:
            duration = now - start
            prefix = '%d/%d commits: ' % (current, total)
            suffix = ' Duration: %s' % str(duration)

            print_progress_bar(current, total, prefix=prefix, suffix=suffix)

    def find_latest_commit_for_head(self, head):
        rev_list = self.git_repository.git.execute(['git', 'rev-list', f'{head.name}', '--'])
        rev_list = rev_list.split('\n')
        return Commit.new_from_sha(self.git_repository, hex_to_bin(rev_list[0]))

    def find_issue_snapshots_by_commit(self, rev):
        issue_snapshots = self._deserialize_issue_snapshots_from_db(rev)
        # Need to fix this, so that commits are returned in reverse order.
        result = dict()

        for issue_snapshot in issue_snapshots:
            if issue_snapshot.commit not in result:
                result[issue_snapshot.commit] = list()
            result[issue_snapshot.commit].append(issue_snapshot)

        return result

    def build_history(self, rev=None, issue_ids=None):

        if not self.git_repository.heads:
            raise NoCommitsError

        history = dict()
        issue_snapshots = self._deserialize_issue_snapshots_from_db(rev)
        for issue_snapshot in issue_snapshots:

            issue_id = issue_snapshot.issue_id
            if issue_ids is None or issue_id in issue_ids:
                if issue_id not in history:
                    history[issue_id] = Issue(issue_id, history)
                history[issue_id].update(issue_snapshot)

        for head in self.git_repository.heads:
            head_commit = self.find_latest_commit_for_head(head)

            head_issue_snapshots = self.get_issue_snapshots_for_commit(head_commit)
            head_issue_snapshot_ids = [issue_snapshot.issue_id for issue_snapshot in head_issue_snapshots]
            for issue_id, issue in history.items():

                if issue_id in head_issue_snapshot_ids:
                    issue.open_in.add(head.name)

        return history

    def get_all_issues(self, rev=None):
        return self.build_history(rev)

    def get_open_issues(self, rev=None):
        history = self.build_history(rev)
        return {issue_id: issue for issue_id, issue in history.items() if issue.status == 'Open'}

    def get_closed_issues(self, rev=None):
        history = self.build_history(rev)
        return {issue_id: issue for issue_id, issue in history.items() if issue.status == 'Closed'}

    @property
    def all_issues(self):
        return self.get_all_issues()

    def _serialize_issue_snapshots_to_db(self, commit_hexsha, issue_snapshots):
        row_values = [(commit_hexsha, issue.issue_id, json.dumps(issue.data)) for issue in issue_snapshots]
        with closing(sqlite3.connect(self.issue_dir + '/issues.db')) as connection:
            cursor = connection.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS IssueSnapshot(commit_sha TEXT, issue_id TEXT, json_data BLOB)")
            cursor.executemany("INSERT INTO IssueSnapshot VALUES(?, ?, ?)", row_values)
            connection.commit()

    def get_issue_snapshots_for_commit(self, commit):

        with closing(sqlite3.connect(self.issue_dir + '/issues.db')) as connection:

            result = list()

            cursor = connection.cursor()
            cursor.row_factory = dict_factory
            cursor.execute("CREATE TABLE IF NOT EXISTS IssueSnapshot(commit_sha TEXT, issue_id TEXT, json_data BLOB)")

            row_values = cursor.execute(
                """
                SELECT * FROM IssueSnapshot WHERE commit_sha=?
                """, (commit.hexsha, )).fetchall()

            for row_value in row_values:
                data = json.loads(row_value['json_data'])
                issue_snapshot = IssueSnapshot(commit, data)
                result.append(issue_snapshot)

            return result

    def _deserialize_issue_snapshots_from_db(self, rev=None):
        result = list()

        with closing(sqlite3.connect(self.issue_dir + '/issues.db')) as connection:
            cursor = connection.cursor()
            cursor.row_factory = dict_factory
            cursor.execute("CREATE TABLE IF NOT EXISTS IssueSnapshot(commit_sha TEXT, issue_id TEXT, json_data BLOB)")
            if rev is None:
                row_values = cursor.execute("SELECT * FROM IssueSnapshot").fetchall()
            else:
                row_values = cursor.execute("SELECT * FROM IssueSnapshot").fetchall()

            for row_value in row_values:
                commit = Commit(self.git_repository, hex_to_bin(row_value['commit_sha']))
                data = json.loads(row_value['json_data'])
                issue_snapshot = IssueSnapshot(commit, data)
                result.append(issue_snapshot)

            return result
