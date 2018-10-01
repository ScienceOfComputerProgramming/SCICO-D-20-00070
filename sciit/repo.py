# -*- coding: utf-8 -*-

import markdown2
import os
import stat
import pkg_resources

from shutil import copyfile
from datetime import datetime

from git import Repo

from sciit import IssueListInCommit
from sciit.errors import EmptyRepositoryError, NoCommitsError
from sciit.commit import find_issues_in_commit
from sciit.functions import write_last_issue_commit_sha, get_last_issue_commit_sha, get_sciit_ignore_path_spec
from sciit.cli.functions import print_progress_bar

__all__ = ('IssueRepo', )


class IssueRepo(Repo):

    def __init__(self, issue_dir=None, path=None):
        if path:
            super(IssueRepo, self).__init__(path=path)
        else:
            super(IssueRepo, self).__init__(search_parent_directories=True)
        if issue_dir:
            self.issue_dir = issue_dir
        else:
            self.issue_dir = self.git_dir + '/issue'
        self.issue_objects_dir = self.issue_dir + '/objects'
        self.cli = False

    def is_init(self):
        return os.path.exists(self.issue_dir)

    def sync(self):
        """
        Ensures that the issue repository issue_commits are synced with the git commits such that there is a
        issue_commit for every commit in the git repository.
        """
        if not self.heads:
            raise NoCommitsError

        last_issue_commit = get_last_issue_commit_sha(self.issue_dir)
        commits = list(self.iter_commits('--all'))

        latest_commit = commits[0].hexsha
        revision = last_issue_commit + '..' + latest_commit
        str_commits = self.git.execute(['git', 'rev-list', revision])
        ignored_files = get_sciit_ignore_path_spec(self)

        # uses git.execute because iter_commits generator cannot correctly identify false or empty list.
        if str_commits != '':
            commits = list(self.iter_commits(revision))

            for commit in reversed(commits):
                issues = find_issues_in_commit(self, commit, ignore_files=ignored_files)
                IssueListInCommit.create_from_commit_and_issues(self, commit, issues)

            write_last_issue_commit_sha(self.issue_dir, latest_commit)

    def reset(self):
        def onerror(func, path, excp_info):
            os.chmod(path, stat.S_IWUSR)
            func(path)

        if self.is_init():
            import shutil
            shutil.rmtree(self.issue_dir, onerror=onerror)
        else:
            raise EmptyRepositoryError

    def setup_file_system_resources(self):
        os.makedirs(self.issue_dir)
        os.makedirs(self.issue_objects_dir)

        open(self.issue_dir + '/HISTORY', 'w').close()
        open(self.issue_dir + '/LAST', 'w').close()

        self._install_hook('post-commit')
        self._install_hook('post-merge')
        self._install_hook('post-checkout')

    def _install_hook(self, hook_name):
        git_hooks_dir = self.git_dir + '/hooks/'
        if not os.path.exists(git_hooks_dir):
            os.makedirs(git_hooks_dir)

        source_resource = pkg_resources.resource_filename('sciit.hooks', hook_name)
        destination_path = git_hooks_dir + hook_name
        copyfile(source_resource, destination_path)
        st = os.stat(destination_path)
        os.chmod(destination_path, st.st_mode | stat.S_IEXEC)

    def iter_issue_commits(self, rev=None, paths='', **kwargs):
        """
        A list of IssueCommit objects representing the history of a given ref/commit.

        :param rev:
            revision specifier, see git-rev-parse for viable options.
            If None, the active branch will be used.

        :param paths:
            is an optional path or a list of paths to limit the returned commits to
            Commits that do not contain that path or the paths will not be returned.

        :param kwargs:
            Arguments to be passed to git-rev-list - common ones are
            max_count and skip

        :note: to receive only commits between two named revisions, use the
            "revA...revB" revision specifier

        :return: ``git.Commit[]``
        """
        commits = self.iter_commits(rev, paths, **kwargs)
        for commit in commits:
            yield IssueListInCommit.create_from_binsha(self, commit.binsha)

    def print_commit_progress(self, now, start, current, total):
        if self.cli:
            duration = now - start
            prefix = '%d/%d commits: ' % (current, total)
            suffix = ' Duration: %s' % str(duration)

            print_progress_bar(current, total, prefix=prefix, suffix=suffix)

    def cache_issue_commits_from_all_commits(self):
        if len(self.heads) < 1:
            raise NoCommitsError

        start = datetime.now()
        commits_scanned = 0

        # get all commits on all branches, enforcing the topology order of parents to children.
        all_commits = self.iter_commits(['--all', '--topo-order', '--reverse'])
        num_commits = int(self.git.execute(['git', 'rev-list', '--all', '--count']))
        ignored_files = get_sciit_ignore_path_spec(self)

        for commit in all_commits:
            commits_scanned += 1

            self.print_commit_progress(datetime.now(), start, commits_scanned, num_commits)
            issues = find_issues_in_commit(self, commit, ignore_files=ignored_files)



            IssueListInCommit.create_from_commit_and_issues(self, commit, issues)

        if all_commits:
            write_last_issue_commit_sha(self.issue_dir, self.head.commit.hexsha)
        else:
            raise NoCommitsError

    def find_latest_issue_commit_for_head(self, rev, head, top):
        if rev is None:
            return IssueListInCommit.create_from_hexsha(self, head.commit.hexsha)
        else:
            rev_list = self.git.execute(['git', 'rev-list', f'{head.name}', '--'])
            if top.hexsha in rev_list:
                return top
            else:
                return None

    def build_history(self, rev=None):

        if not self.heads:
            raise NoCommitsError

        history = {}
        time_format = '%a %b %d %H:%M:%S %Y %z'

        if rev is None:
            issue_commits = self.iter_issue_commits('--branches')
        else:
            issue_commits = self.iter_issue_commits(rev)

        issue_commits = list(issue_commits)

        for issue_commit in issue_commits:

            in_branches = \
                self.git.execute(['git', 'branch', '--contains', issue_commit.commit.hexsha])\
                    .replace('*', '')\
                    .replace(' ', '').split('\n')

            for issue in issue_commit.issues:
                if issue.id not in history:
                    history[issue.id] = IssueHistory(issue.id)

                history[issue.id].update(issue, issue_commit, in_branches)

        for head in self.heads:
            head_issue_commit = self.find_latest_issue_commit_for_head(rev, head, issue_commits[0])

            if head_issue_commit is None:
                continue

            for issue in head_issue_commit.issues:
                if issue.id in history:
                    history[issue.id].open_in.add(head.name)

        return history

    def get_all_issues(self, rev=None):
        return self.build_history(rev)

    def get_open_issues(self, rev=None):
        history = self.build_history(rev)
        return {id: issue for id, issue in history.items() if issue.status == 'Open'}

    def get_closed_issues(self, rev=None):
        history = self.build_history(rev)
        return {id: issue for id, issue in history.items() if issue.status == 'Closed'}

    @property
    def all_issues(self):
        return self.get_all_issues()

    @property
    def open_issues(self):
        return self.get_open_issues()

    @property
    def closed_issues(self):
        return self.get_closed_issues()


class IssueHistory(object):

    def __init__(self, issue_id):

        self.issue_id = issue_id

        self.issue_and_issue_commits = list()

        self.open_in = set()

    @property
    def oldest_issue_and_issue_commit(self):
        return self.issue_and_issue_commits[-1]

    @property
    def newest_issue_and_issue_commit(self):
        return self.issue_and_issue_commits[0]

    @property
    def newest_issue_commit(self):
        return self.newest_issue_and_issue_commit[1]

    @property
    def oldest_issue_commit(self):
        return self.oldest_issue_and_issue_commit[1]

    @property
    def last_author(self):
        return self.newest_issue_commit.commit.author.name

    @property
    def creator(self):
        return self.oldest_issue_commit.commit.author.name

    @property
    def created_date(self):
        return self.oldest_issue_commit.date_string

    @property
    def last_authored_date(self):
        return self.newest_issue_commit.date_string

    def newest_value_of_issue_property(self, p):
        for issue_and_issue_commit in self.issue_and_issue_commits:
            if hasattr(issue_and_issue_commit[0], p):
                return getattr(issue_and_issue_commit[0], p)
        return None

    @property
    def hexsha(self):
        return self.newest_value_of_issue_property('hexsha')

    @property
    def title(self):
        return self.newest_value_of_issue_property('title')

    @property
    def description(self):
        return self.newest_value_of_issue_property('description')

    @property
    def description_as_html(self):
        return markdown2.markdown(self.description)

    @property
    def assignees(self):
        return self.newest_value_of_issue_property('assignees')

    @property
    def due_date(self):
        return self.newest_value_of_issue_property('due_date')

    @property
    def label(self):
        return self.newest_value_of_issue_property('label')

    @property
    def weight(self):
        return self.newest_value_of_issue_property('weight')

    @property
    def priority(self):
        return self.newest_value_of_issue_property('priority')

    @property
    def file_paths(self):
        result = dict()
        for issue, issue_commit, branches in self.issue_and_issue_commits:
            for branch in branches:
                if branch not in result:
                    result[branch] = issue.data['filepath']
        return result

    @property
    def file_path(self):
        return self.newest_issue_and_issue_commit[0].data['filepath']

    @property
    def participants(self):
        result = set()
        for issue_and_issue_commit in self.issue_and_issue_commits:
            result.add(issue_and_issue_commit[1].author_name)
        return result

    @property
    def status(self):
        return 'Open' if len(self.open_in) > 0 else 'Closed'

    @property
    def closing_commit(self):
        if self.status == 'Closed':
            _, last_issue_commit, _ = self.newest_issue_and_issue_commit
            child = last_issue_commit.children[0]
            return child
        else:
            return None

    @property
    def closer(self):
        return self.closing_commit.author.name if self.closing_commit else None

    @property
    def closed_date(self):
        time_format = '%a %b %d %H:%M:%S %Y %z'
        return self.closing_commit.authored_datetime.strftime(time_format) if self.closing_commit else None

    @property
    def closing_summary(self):
        return self.closing_commit.summary if self.closing_commit else None

    @property
    def activity(self):
        result = list()
        for issue, issue_commit, _ in self.issue_and_issue_commits:
            result.append(
                {
                    'commitsha': issue_commit.commit.hexsha,
                    'date': issue_commit.date_string,
                    'author': issue_commit.author_name,
                    'summary': issue_commit.commit.summary})

        if self.status == 'Closed':

            closing_activity = \
                {
                    'commitsha': self.closing_commit.hexsha,
                    'date': self.closed_date,
                    'author': self.closer,
                    'summary': self.closing_summary + ' (closed)'
                }
            result.insert(0, closing_activity)

        return result


    @property
    def revisions(self):
        result = list()

        if self.status == 'Closed':
            result.append(
                {
                    'issuesha': self.closing_commit.hexsha,
                    'date': self.closed_date,
                    'author': self.closing_commit.author.name,
                    'changes': {'status': 'Closed'}
                }
            )

        for newer, older in zip(self.issue_and_issue_commits[:-1], self.issue_and_issue_commits[1:]):
            newer_issue = newer[0]
            older_issue = older[0]

            changes = dict()
            for k, v in newer_issue.data.items():
                if k not in older_issue.data or older_issue.data[k] != v:
                    changes[k] = v

            if 'hexsha' in changes:
                del changes['hexsha']

            if len(changes) > 0:

                revision = {
                    'issuesha': newer[1].commit.hexsha,
                    'date': newer[1].date_string,
                    'author': newer[1].author_name,
                    'changes': changes
                }
                result.append(revision)

        original_values = self.oldest_issue_and_issue_commit[0].data
        if 'hexsha' in original_values:
            del original_values['hexsha']

        oldest_version = {
            'issuesha': self.oldest_issue_commit.commit.hexsha,
            'date': self.oldest_issue_commit.date_string,
            'author': self.oldest_issue_commit.author_name,
            'changes': original_values
        }
        result.append(oldest_version)

        return result

    @property
    def size(self):
        return sum([issue_and_issue_commit[1].size for issue_and_issue_commit in self.issue_and_issue_commits])

    @property
    def in_branches(self):
        result = set()
        for issue_and_issue_commit in self.issue_and_issue_commits:
            result.update(issue_and_issue_commit[2])
        return result

    def update(self, issue, issue_commit, branches):
        """
        Update the content of the issue history, based on newly discovered, *older* information.
        """
        self.issue_and_issue_commits.append((issue, issue_commit, branches))
