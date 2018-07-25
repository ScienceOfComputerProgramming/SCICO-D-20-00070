# -*- coding: utf-8 -*-
"""Module that contains the definition of the issue repo.

:@author: Nystrom Edwards
:Created: 21 June 2018
"""
import os
import re
import stat
import pkg_resources

from shutil import copyfile
from datetime import datetime

from git import Repo

from sciit import IssueTree, IssueCommit, Issue
from sciit.errors import EmptyRepositoryError, NoCommitsError
from sciit.tree import find_issues_in_tree
from sciit.regex import PYTHON
from sciit.functions import write_last_issue, get_last_issue
from sciit.cli.functions import print_progress_bar

__all__ = ('IssueRepo', )


class IssueRepo(Repo):
    """IssueRepo objects represent the git and issue repository.
    Inherits from `GitPython.Repo <https://gitpython.readthedocs.io/en/2.1.10/\
    reference.html#module-git.repo.base>`_.
    """

    def __init__(self, issue_dir=None):
        """Initialize a newly instanced IssueRepo

        Args:
            :(str) issue_dir: string representing location of issue\
            repository *default='.git/issue'*  
        """
        super(IssueRepo, self).__init__(search_parent_directories=True)
        if issue_dir:
            self.issue_dir = issue_dir
        else:
            self.issue_dir = self.git_dir + '/issue'
        self.issue_objects_dir = self.issue_dir + '/objects'
        self.cli = False

    def is_init(self):
        """
        Detect if the git sciit folders are initialised

        Returns:
            :bool: true if folder exists, false otherwise
        """
        return os.path.exists(self.issue_dir)

    def sync(self):
        """
        """
        last_issue_commit = get_last_issue(self)
        commits = list(self.iter_commits('--all'))
        latest_commit = commits[0].hexsha
        revision = last_issue_commit + '..' + latest_commit
        str_commits = self.git.execute(['git', 'rev-list', revision])

        # uses git.execute because iter_commits generator cannot
        # correctly identify false or empty list.
        if str_commits != '':
            commits = list(self.iter_commits(revision))

            for commit in reversed(commits):
                issues = find_issues_in_tree(self, commit.tree)
                itree = IssueTree.create(self, issues)
                IssueCommit.create(self, commit, itree)

            write_last_issue(self.issue_dir, latest_commit)

    def reset(self):
        """
        Resets the git sciit folders 

        Raises:
            :EmptyRepositoryError: if repo is not initialized
        """
        def onerror(func, path, excp_info):
            os.chmod(path, stat.S_IWUSR)
            func(path)

        if self.is_init():
            import shutil
            shutil.rmtree(self.issue_dir, onerror=onerror)
        else:
            raise EmptyRepositoryError

    def setup(self):
        """
        Creates the git sciit folders and files and installs the necesary
        git hooks in the .git/hooks/ folder
        """
        os.makedirs(self.issue_dir)
        os.makedirs(self.issue_objects_dir)

        # create history file
        history_file = self.issue_dir + '/HISTORY'
        f = open(history_file, 'w')
        f.close()
        # create last issue reference file
        last_issue_file = self.issue_dir + '/LAST'
        f = open(last_issue_file, 'w')
        f.close()

        # check git hook directory
        git_hooks_dir = self.git_dir + '/hooks/'
        if not os.path.exists(git_hooks_dir):
            os.makedirs(git_hooks_dir)

        # install post-commit hook
        post_commit_hook = pkg_resources.resource_filename(
            'sciit.hooks', 'post-commit')
        post_commit_git_hook = git_hooks_dir + 'post-commit'
        copyfile(post_commit_hook, post_commit_git_hook)
        st = os.stat(post_commit_git_hook)
        os.chmod(post_commit_git_hook, st.st_mode | stat.S_IEXEC)

        # install post-merge hook
        post_merge_hook = pkg_resources.resource_filename(
            'sciit.hooks', 'post-merge')
        post_merge_git_hook = git_hooks_dir + 'post-merge'
        copyfile(post_merge_hook, post_merge_git_hook)
        st = os.stat(post_merge_git_hook)
        os.chmod(post_merge_git_hook, st.st_mode | stat.S_IEXEC)

        # install post-checkout hook
        post_checkout_hook = pkg_resources.resource_filename(
            'sciit.hooks', 'post-checkout')
        post_checkout_git_hook = git_hooks_dir + 'post-checkout'
        copyfile(post_checkout_hook, post_checkout_git_hook)
        st = os.stat(post_checkout_git_hook)
        os.chmod(post_checkout_git_hook, st.st_mode | stat.S_IEXEC)

    def iter_issue_commits(self, rev=None, paths='', **kwargs):
        """A list of IssueCommit objects representing the history of a given ref/commit

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

        :return: ``git.Commit[]``"""
        commits = self.iter_commits(rev, paths, **kwargs)
        for commit in commits:
            yield IssueCommit(self, commit.binsha)

    def print_commit_progress(self, now, start, current, total):
        """
        Prints the progress of the iterating commits

        Args:
            :(datetime) now: The current system time
            :(datetime) start: The system time when the process started
            :(int) current: the current issue processed
            :(int) total: total number of issues to be processes

        Shows:
            :Commit status: The current commit iteration
            :Progress bar: Progress of the operation
            :Precentage: The percentage of the operation complete
            :Duration: How long the operation has been running

        """
        if self.cli:
            duration = now - start
            prefix = '%d/%d commits: ' % (current, total)
            suffix = ' Duration: %s' % str(duration)
            print_progress_bar(
                current, total, prefix=prefix, suffix=suffix)

    def build(self):
        """
        Builds the issue repository from past commits on all branches

        Raises:
            :NoCommitsError: if the git repository has no commits

        Optionally:
            :Shows Progress in Shell: if repo is used with command line interface
        """

        '''
        @issue Better Build Performance
        @description
            Find some method to increase the speed of this algorithm for finding
            issue data in commit trees. Check if the GitPython library has good
            multithreading support so that we can use thread to build issues.
            Essentially this should be done here as this is a time consuming
            process and can lead to a waste of developer time.

            Threading is a good solution here because the commits and the references
            that are used to build them are stored as text in a series of files.
            It does not matter what order the files are written to the issue 
            repository cache once they contain the correct references.
        @assigned to: nystrome
        @priority: medium 6/10
        '''
        start = datetime.now()
        commits_scanned = 0

        if len(self.heads) > 0:
            # get all commits on the all branches
            all_commits = list(self.iter_commits('--all'))
            num_commits = len(all_commits)

            # reversed to start at the first commit
            for commit in reversed(all_commits):
                commits_scanned += 1

                self.print_commit_progress(
                    datetime.now(), start, commits_scanned, num_commits)

                issues = find_issues_in_tree(self, commit.tree)
                itree = IssueTree.create(self, issues)
                IssueCommit.create(self, commit, itree)
        else:
            raise NoCommitsError
        write_last_issue(self.issue_dir, all_commits[0].hexsha)

    def build_history(self, rev=None, paths='', **kwargs):
        """
        Builds the issue history from past commits on path specified
        or all branches

        Raises:
            :NoCommitsError: if the git repository has no commits
            :GitCommandError: if the rev supplied is not valid
        """
        if self.heads:
            history = {}
            time_format = '%a %b %d %H:%M:%S %Y %z'
            # get all commits on the all branches
            if rev is not None:
                icommits = list(self.iter_issue_commits(rev, paths, **kwargs))
            else:
                icommits = list(self.iter_issue_commits('--branches'))

            for icommit in icommits:
                """
                @issue specify files related to issue
                @description
                    It may be useful to specify the files that are related to the issue.
                    This way when we are building the history, if those files specified
                    are present we can then use the commit data only from those files to
                    show the commit activity. This will show explicitly that work has been
                    done on those files.
                @label feature-enhancement
                @priority medium
                """
                for issue in icommit.issuetree.issues:
                    in_branches = self.find_present_branches(
                        icommit.commit.hexsha)
                    # issue first appearance in history build the general
                    # indexes needed to record complex information
                    if issue.id not in history:
                        history[issue.id] = issue.data
                        history[issue.id]['size'] = issue.size
                        history[issue.id]['creator'] = icommit.commit.author.name
                        history[issue.id]['created_date'] = \
                            icommit.commit.authored_datetime.strftime(
                            time_format)
                        history[issue.id]['last_author'] = icommit.commit.author.name
                        history[issue.id]['last_authored_date'] = \
                            icommit.commit.authored_datetime.strftime(
                            time_format)
                        history[issue.id]['revisions'] = set()
                        history[issue.id]['revisions'].add(issue.hexsha)
                        history[issue.id]['activity'] = []
                        activity = {'date': icommit.commit.authored_datetime.strftime(time_format),
                                    'author': icommit.commit.author.name,
                                    'summary': icommit.commit.summary}
                        history[issue.id]['activity'].append(activity)
                        history[issue.id]['participants'] = set()
                        history[issue.id]['participants'].add(
                            icommit.commit.author.name)
                        history[issue.id]['in_branches'] = set()
                        history[issue.id]['in_branches'].update(in_branches)
                        # for future use filling branch status
                        history[issue.id]['open_in'] = set()
                        history[issue.id]['filepath'] = set()
                        history[issue.id]['descriptions'] = []
                        if 'description' in history[issue.id]:
                            history[issue.id]['descriptions'].append(
                                {'change': issue.description,
                                 'author': icommit.commit.author.name,
                                 'date': icommit.commit.authored_datetime.strftime(time_format)
                                 }
                            )
                    # update the history information when more instances
                    # of the issue is found
                    else:
                        history[issue.id]['size'] += issue.size
                        history[issue.id]['creator'] = icommit.commit.author.name
                        history[issue.id]['created_date'] = \
                            icommit.commit.authored_datetime.strftime(
                            time_format)
                        history[issue.id]['participants'].add(
                            icommit.commit.author.name)
                        history[issue.id]['in_branches'].update(in_branches)
                        activity = {'date': icommit.commit.authored_datetime.strftime(time_format),
                                    'author': icommit.commit.author.name,
                                    'summary': icommit.commit.summary}
                        history[issue.id]['activity'].append(activity)
                        history[issue.id]['revisions'].add(issue.hexsha)
                        if 'description' in history[issue.id]:
                            if hasattr(issue, 'description'):
                                if issue.description != history[issue.id]['description']:
                                    history[issue.id]['description'] = issue.description
                                    history[issue.id]['descriptions'].append(
                                        {'change': issue.description,
                                         'author': icommit.commit.author.name,
                                         'date': icommit.commit.authored_datetime.strftime(time_format)
                                         }
                                    )
                        else:
                            if hasattr(issue, 'description'):
                                history[issue.id]['descriptions'].append(
                                    {'change': issue.description,
                                     'author': icommit.commit.author.name,
                                     'date': icommit.commit.authored_datetime.strftime(time_format)
                                     }
                                )

            # fills the open branch set with branch status using the
            # issue trees at the head of each branch
            for head in self.heads:
                icommit = IssueCommit(self, head.commit.hexsha)
                for issue in icommit.issuetree.issues:
                    history[issue.id]['open_in'].add(head.name)
                    history[issue.id]['filepath'].add(
                        issue.data['filepath'] + ' @' + head.name)

            # sets the issue status based on its open status
            # in other branches
            for issue in history.values():
                if issue['open_in']:
                    issue['status'] = 'Open'
                else:
                    issue['status'] = 'Closed'
        else:
            raise NoCommitsError

        return history

    def find_present_branches(self, commit_sha):
        """
        A function that helps find the branches that this commit is
        present in which can be used to define where issues are present

        Args:
            :(str) commit_sha: The commit hexsha to look for
        """
        branches_present = self.git.execute(
            ['git', 'branch', '--contains', commit_sha])
        branches_present = branches_present.replace(
            '*', '').replace(' ', '')
        branches_present = branches_present
        branches_present = branches_present.split('\n')
        return branches_present

    @property
    def all_issues(self):
        """Finds all the issues in the repo 

        Returns:
            :(dict) history: dictionary of the complex information \
            between the issue tracker and the source control
        """
        history = self.build_history()
        return history

    @property
    def open_issues(self):
        """Finds all the open issues in the repo 

        Returns:
            :(dict) history: dictionary of the complex information \
            between the issue tracker and the source control
        """
        history = self.build_history()
        history = {key: val for key,
                   val in history.items() if val['status'] == 'Open'}
        return history

    @property
    def closed_issues(self):
        """Finds all the closed issues in the repo.

        Returns:
            :(dict) history: dictionary of the complex information \
            between the issue tracker and the source control
        """
        history = self.build_history()
        history = {key: val for key,
                   val in history.items() if val['status'] == 'Closed'}
        return history
