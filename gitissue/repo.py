# -*- coding: utf-8 -*-
"""Module that contains the definition of the issue repo.

:@author: Nystrom Edwards
:Created: 21 June 2018
"""
import os
import re

from datetime import datetime

from git import Repo

from gitissue import tools, IssueTree, IssueCommit
from gitissue.errors import EmptyRepositoryError, NoCommitsError
from gitissue.tree import find_issues_in_tree
from gitissue.regex import PYTHON_MULTILINE_HASH, PYTHON_MULTILINE_DOCSTRING

__all__ = ('IssueRepo',)

patterns = [PYTHON_MULTILINE_HASH, PYTHON_MULTILINE_DOCSTRING]


class IssueRepo(Repo):
    """IssueRepo objects represent the git and issue repository.
    """

    def __init__(self):
        """Initialize a newly instanced IssueRepo
        *inherited from GitPython Repo*
        :note:
            Add the issue and objects directory to the definition
            of the repository
        """
        super(IssueRepo, self).__init__()
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
            tools.print_progress_bar(
                commits_scanned, num_commits, prefix=prefix, suffix=suffix)

        if len(self.heads) > 0:
            # get all commits on the master branch
            # TODO: figure out if it is needed to find in other branches
            # like a development branch!
            all_commits = list(self.iter_commits('master'))
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
