# -*- coding: utf-8 -*-
"""Module that contains the definition of the issue repo.

:@author: Nystrom Edwards
:Created: 21 June 2018
"""
import os
import re

from datetime import datetime

from git import Repo

from gitissue import IssueTree, IssueCommit, Issue
from gitissue.errors import EmptyRepositoryError, NoCommitsError
from gitissue.tree import find_issues_in_tree
from gitissue.regex import PYTHON_MULTILINE_DOCSTRING
from gitissue.functions import get_issue_history
from gitissue.cli.functions import print_progress_bar

__all__ = ('IssueRepo', 'get_all_issues',
           'get_open_issues', 'get_closed_issues')

patterns = [PYTHON_MULTILINE_DOCSTRING, ]


def get_all_issues(repo, branch=None):
    """Finds all the issues in the repo in comparison to open
    issues on the specified branch. 

    Args:
        :(Repo) repo: the issue repository
        :(str) branch: the head of the branch to search \
        *head of current branch if None*

    Returns:
        :list(Issue) issues: list of all issues specified \
        by branch
    """
    issues = []
    history = get_issue_history(repo)
    for issue in history:
        issues.append(Issue(repo, issue['sha']))
    issues.sort()
    open_issues = get_open_issues(repo, branch)
    for issue in issues:
        if issue in open_issues:
            issue.status = 'Open'
        else:
            issue.status = 'Closed'
    return issues


def get_open_issues(repo, branch=None):
    """Finds all the open issues in the repo that are on a 
    specified branch. 

    Args:
        :(Repo) repo: the issue repository
        :(str) branch: the head of the branch to search \
        *head of current branch if None*

    Returns:
        :list(Issue) issues: list of all open issues specified \
        by branch
    """
    if branch is not None:
        head_sha = repo.heads[branch].commit.hexsha
    else:
        head_sha = repo.head.commit.hexsha
    head_icommit = IssueCommit(repo, head_sha)
    open_issues = head_icommit.issuetree.issues
    for issue in open_issues:
        issue.status = 'Open'
    return open_issues


def get_closed_issues(repo, branch=None):
    """Finds all the closed issues in the repo in comparison to open
    issues on the specified branch. 

    Args:
        :(Repo) repo: the issue repository
        :(str) branch: the head of the branch to search \
        *head of current branch if None*

    Returns:
        :list(Issue) issues: list of all closed issues specified \
        by branch
    """
    all_issues = get_all_issues(repo, branch)
    open_issues = get_open_issues(repo, branch)
    closed_issues = [x for x in all_issues if x not in open_issues]
    return closed_issues


class IssueRepo(Repo):
    """IssueRepo objects represent the git and issue repository.
    Inherits from `GitPython.Repo <https://gitpython.readthedocs.io/en/stable/reference.html#module-git.repo.base>`_.
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
        Creates the git-issue folders 
        """
        os.makedirs(self.issue_dir)
        os.makedirs(self.issue_objects_dir)

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

    def build(self):
        """
        Builds the git-issue repository from past commits on the
        master branch

        Raises:
            :NoCommitsError: if the git repository has no commits

        Optionally:
            :Shows Progress in Shell: if repo is used with command line interface
        """
        start = datetime.now()
        commits_scanned = 0

        def print_commit_progress(now, start):
            """
            Prints the progress of the building of the repository from past commits

            Args:
                :(datetime) now: The current system time
                :(datetime) start: The system time when the process started

            Shows:
                :Commit status: The current commit iteration
                :Progress bar: Progress of the operation
                :Precentage: The percentage of the operation complete
                :Duration: How long the operation has been running

            """
            duration = now - start
            prefix = '%s/%s commits: ' % (commits_scanned, str(num_commits))
            suffix = ' Duration: %s' % str(duration)
            print_progress_bar(
                commits_scanned, num_commits, prefix=prefix, suffix=suffix)

        if len(self.heads) > 0:
            # get all commits on the all branches
            # TODO: figure out if it is needed to find in other branches
            # like a development branch!
            all_commits = list(self.iter_commits('--all'))
            num_commits = len(all_commits)

            # reversed to start at the first commit
            for commit in reversed(all_commits):
                commits_scanned += 1

                if self.cli:
                    print_commit_progress(datetime.now(), start)

                issues = find_issues_in_tree(self, commit.tree, patterns)
                itree = IssueTree.create(self, issues)
                IssueCommit.create(self, commit, itree)
        else:
            raise NoCommitsError
