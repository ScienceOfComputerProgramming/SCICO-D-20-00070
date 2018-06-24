import os
import re
import sys

from datetime import datetime
from collections import Counter

from git import Repo

from gitissue import tools
from gitissue import IssueTree
from gitissue.errors import *
from gitissue.regex import MULTILINE_HASH_PYTHON_COMMENT

__all__ = ('IssueRepo',)


def find_issues_in_commit_tree(commit_tree, parent=None):
    matches = []
    if commit_tree.type != 'submodule':
        for item in commit_tree:
            if item.type == 'blob':
                # read the data contained in that file
                try:
                    object_contents = item.data_stream.read().decode('utf-8')
                    matched_issues = re.findall(
                        MULTILINE_HASH_PYTHON_COMMENT, object_contents)
                    result = {'filepath': str(item.path),
                              'issues': matched_issues}
                    # if a string match for issue found
                    if matched_issues is not None:
                        matches.append(result)
                except UnicodeDecodeError:
                    pass
            else:
                matches.append(find_issues_in_commit_tree(item, item.path))
    return matches


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
        repo = IssueRepo()
        return os.path.exists(repo.issue_dir)

    def reset(self):
        if self.is_init():
            import shutil
            shutil.rmtree(self.issue_dir)
        else:
            raise EmptyRepositoryError()

    def setup(self):
        os.makedirs(self.issue_dir)
        os.makedirs(self.issue_objects_dir)

    def build(self):
        # from collections import Counter

        start = datetime.now()
        commits_scanned = 0

        # TODO change the patterns here if needed
        # initialize to the current repo
        all_matches = []

        def print_commit_progress(now, start):
            duration = now - start
            prefix = '%s/%s commits: ' % (commits_scanned, str(num_commits))
            suffix = ' Duration: %s' % str(duration)
            tools.print_progress_bar(
                commits_scanned, num_commits, prefix=prefix, suffix=suffix)

        # the repo has no heads therefore no commits
        # TODO this may need changeing
        if len(self.heads) > 0:
            # get all commits on the master branch
            all_commits = list(self.iter_commits('master'))
            num_commits = len(all_commits)
            for commit in all_commits:
                commits_scanned += 1

                # prints the progress
                if self.cli:
                    print_commit_progress(datetime.now(), start)

                # finds all the issues in the commit
                result = find_issues_in_commit_tree(commit.tree)

                # of the issues found find the number of occurances
                # of the same pattern
                # result = Counter(result)
                all_matches.append(result)
                IssueTree.create(self, result)

        else:
            raise NoCommitsError
        print(all_matches)
        return
