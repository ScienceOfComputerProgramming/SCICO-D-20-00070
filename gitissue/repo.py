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

from gitissue import IssueTree, IssueCommit, Issue
from gitissue.errors import EmptyRepositoryError, NoCommitsError
from gitissue.tree import find_issues_in_tree
from gitissue.regex import PYTHON
from gitissue.cli.functions import print_progress_bar

__all__ = ('IssueRepo', )


class IssueRepo(Repo):
    """IssueRepo objects represent the git and issue repository.
    Inherits from `GitPython.Repo <https://gitpython.readthedocs.io/en/2.1.10/\
    reference.html#module-git.repo.base>`_.
    """

    def __init__(self):
        """Initialize a newly instanced IssueRepo
        *inherited from GitPython Repo*
        :note:
            Add the issue and objects directory to the definition
            of the repository
        """
        super(IssueRepo, self).__init__(search_parent_directories=True)
        self.issue_dir = self.git_dir + '/issue'
        self.issue_objects_dir = self.issue_dir + '/objects'
        self.cli = False

    def is_init(self):
        """
        Detect if the git-issue folders are initialised

        Returns:
            :bool: true if folder exists, false otherwise
        """
        return os.path.exists(self.issue_dir)

    def reset(self):
        """
        Resets the git-issue folders 

        Raises:
            :EmptyRepositoryError: if repo is not initialized
        """
        if self.is_init():
            import shutil
            shutil.rmtree(self.issue_dir)
        else:
            raise EmptyRepositoryError

    def setup(self):
        """
        Creates the git-issue folders and installs the necesary
        git hooks in the .git/hooks/ folder
        """
        os.makedirs(self.issue_dir)
        os.makedirs(self.issue_objects_dir)
        git_hooks_dir = self.git_dir + '/hooks/'
        if not os.path.exists(git_hooks_dir):
            os.makedirs(git_hooks_dir)
        post_commit_hook = pkg_resources.resource_filename(
            'gitissue.hooks', 'post-commit')
        post_commit_git_hook = git_hooks_dir + 'post-commit'
        copyfile(post_commit_hook, post_commit_git_hook)
        st = os.stat(post_commit_git_hook)
        os.chmod(post_commit_git_hook, st.st_mode | stat.S_IEXEC)

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
        start = datetime.now()
        commits_scanned = 0

        if len(self.heads) > 0:
            # get all commits on the all branches
            all_commits = list(self.iter_commits('--branches'))
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
