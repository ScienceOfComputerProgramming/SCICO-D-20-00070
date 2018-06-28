import os
import re
import sys

from datetime import datetime
from collections import Counter

from git import Repo

from gitissue import tools
from gitissue import IssueTree, IssueCommit
from gitissue.errors import EmptyRepositoryError, NoCommitsError
from gitissue.commit import find_issues_in_commit_tree
from gitissue.regex import MULTILINE_HASH_PYTHON_COMMENT

__all__ = ('IssueRepo',)

patterns = [MULTILINE_HASH_PYTHON_COMMENT, ]


class IssueRepo(Repo):

    def __init__(self):
        super(IssueRepo, self).__init__()
        self.issue_dir = self.git_dir + '/issue'
        self.issue_objects_dir = self.issue_dir + '/objects'
        self.cli = False

    def is_init(self):
        """
        A function that is used to detect if the git-issue folders
        are initialised

        Returns:
            :bool: true if folder exists, false otherwise
        """
        return os.path.exists(self.issue_dir)

    def reset(self):
        if self.is_init():
            import shutil
            shutil.rmtree(self.issue_dir)
        else:
            raise EmptyRepositoryError

    def setup(self):
        os.makedirs(self.issue_dir)
        os.makedirs(self.issue_objects_dir)

    def build(self):
        start = datetime.now()
        commits_scanned = 0

        def print_commit_progress(now, start):
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

                result = find_issues_in_commit_tree(commit.tree, patterns)
                itree = IssueTree.create(self, result)
                IssueCommit.create(self, commit, itree)
        else:
            raise NoCommitsError
        return
