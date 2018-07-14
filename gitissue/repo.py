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
from gitissue.functions import get_issue_history
from gitissue.cli.functions import print_progress_bar

__all__ = ('IssueRepo', 'get_all_issues',
           'get_open_issues', 'get_closed_issues')

patterns = [PYTHON, ]


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
        Creates the git-issue folders and installs the necesary
        git hooks in the .git/hooks/ folder
        """
        os.makedirs(self.issue_dir)
        os.makedirs(self.issue_objects_dir)
        git_hooks_dir = self.git_dir + '/hooks/'

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

                issues = find_issues_in_tree(self, commit.tree, patterns)
                itree = IssueTree.create(self, issues)
                IssueCommit.create(self, commit, itree)
        else:
            raise NoCommitsError

    """
    @issue generate complex history from commits
    @description
        Try to generate the complex history between
        commits in a way that can be inferred from the
        source control
    """

    def build_history(self, rev=None, paths='', **kwargs):
        """
        Builds the issue history from past commits on path specified
        or all branches

        Raises:
            :NoCommitsError: if the git repository has no commits
            :GitCommandError: if the rev supplied is not valid

        Optionally:
            :Shows Progress in Shell: if repo is used with command line interface
        """
        start = datetime.now()
        commits_scanned = 0

        if len(self.heads) > 0:
            history = {}

            # get all commits on the all branches
            if rev is not None:
                icommits = list(self.iter_issue_commits(rev, paths, **kwargs))
            else:
                icommits = list(self.iter_issue_commits('--branches'))
            num_commits = len(icommits)

            for icommit in icommits:
                commits_scanned += 1

                self.print_commit_progress(
                    datetime.now(), start, commits_scanned, num_commits)

                for issue in icommit.issuetree.issues:
                    in_branches = self.find_present_branches(
                        icommit.commit.hexsha)
                    # issue first appearance in history
                    if issue.id not in history:
                        history[issue.id] = issue.data
                        history[issue.id]['creator'] = icommit.commit.author.name
                        history[issue.id]['created_date'] = icommit.commit.authored_datetime
                        history[issue.id]['last_author'] = icommit.commit.author.name
                        history[issue.id]['last_authored_date'] = icommit.commit.authored_datetime
                        history[issue.id]['revisions'] = []
                        history[issue.id]['revisions'].append(issue.hexsha)
                        history[issue.id]['participants'] = set()
                        history[issue.id]['participants'].add(
                            icommit.commit.author.name)
                        history[issue.id]['in_branches'] = set()
                        history[issue.id]['in_branches'].update(in_branches)
                        history[issue.id]['open_in'] = set()
                        if 'description' in history[issue.id]:
                            history[issue.id]['description'] += f'\n -added by:{icommit.commit.author.name}'
                    # update the history information
                    else:
                        history[issue.id]['creator'] = icommit.commit.author.name
                        history[issue.id]['created_date'] = icommit.commit.authored_datetime
                        history[issue.id]['participants'] = set()
                        history[issue.id]['participants'].add(
                            icommit.commit.author.name)
                        history[issue.id]['in_branches'].update(in_branches)
                        # a revision is added to the list
                        if issue.hexsha == history[issue.id]['revisions'][-1]:
                            history[issue.id]['revisions'][-1]

            # fills the open branch set with branch status
            for head in self.heads:
                icommit = IssueCommit(self, head.commit.binsha)
                for issue in icommit.issuetree.issues:
                    history[issue.id]['open_in'].add(head.name)

            # sets the issue status
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
