import os
import re
import sys

from datetime import datetime

from git import Repo

from gitissue import tools

__all__ = ('IssueRepo',)


def find_pattern_in_tree(commit_tree, pattern):
    matches = []
    if commit_tree.type != 'submodule':
        for item in commit_tree:
            if item.type == 'blob':
                # read the data contained in that file
                try:
                    object_contents = item.data_stream.read().decode('utf-8')
                    matched_issues = pattern.findall(object_contents)

                    # if a string match for issue found
                    if matched_issues is not None:
                        matches.extend(matched_issues)
                except UnicodeDecodeError:
                    pass
            else:
                matches.extend(find_pattern_in_tree(
                    item, pattern))
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
            pass
            # TODO Throw an error here
            # print('Issue repository empty\n\ttry running: git issue init')
            # sys.exit(0)

    def setup(self):
        os.makedirs(self.issue_dir)
        os.makedirs(self.issue_objects_dir)

    def build(self):
        # from collections import Counter

        start = datetime.now()
        commits_scanned = 0

        # TODO change the patterns here if needed
        # initialize to the current repo
        pattern = r'(^\s*#.*$)'
        pattern = re.compile(pattern, re.MULTILINE)
        all_matches = []

        def print_commit_progress(now, start):
            duration = now - start
            prefix = '%s/%s commits: ' % (commits_scanned, str(num_commits))
            suffix = ' Duration: %s' % str(duration)
            tools.print_progress_bar(
                commits_scanned, num_commits, prefix=prefix, suffix=suffix)

        # if the repo is not empty
        if not self.bare:
            # get all commits on the master branch
            all_commits = list(self.iter_commits('master'))
            num_commits = len(all_commits)

            for commit in all_commits:
                commits_scanned += 1

                # prints the progress
                if self.cli:
                    print_commit_progress(datetime.now(), start)

                # finds all the issues in the commit
                result = find_pattern_in_tree(commit.tree, pattern)
                all_matches.extend(result)

        else:
            # TODO throw repo bare error
            pass

        return
