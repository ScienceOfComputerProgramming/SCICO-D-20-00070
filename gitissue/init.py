import os
import re
import sys
from datetime import datetime
from git import Repo
from gitissue.tools import system, repotool

repo = Repo()
issue_dir = repo.git_dir + '/issue'
issue_objects_dir = issue_dir + '/objects'


def reset_issue_repo():
    if system.is_init():
        import shutil
        shutil.rmtree(issue_dir)
    else:
        print('Issue repository empty\n\ttry running: git issue init')
        sys.exit(0)


def setup_folders():
    print('Setting up folders...')
    issue_dir = repo.git_dir + '/issue'
    issue_objects_dir = issue_dir + '/objects'
    os.makedirs(issue_dir)
    os.makedirs(issue_objects_dir)


def build_from_past_commits():
    # from collections import Counter

    start = datetime.now()
    commits_scanned = 0

    # initialize to the current repo
    pattern = r'(^\s*#.*$)'
    pattern = re.compile(pattern, re.MULTILINE)
    all_matches = []

    def print_commit_progress(now, start):
        duration = now - start
        prefix = '%s/%s commits: ' % (commits_scanned, str(num_commits))
        suffix = ' Duration: %s' % str(duration)
        system.print_progress_bar(
            commits_scanned, num_commits, prefix=prefix, suffix=suffix)

    # if the repo is not empty
    if not repo.bare:
        # get all commits on the master branch
        all_commits = list(repo.iter_commits('master'))
        num_commits = len(all_commits)

        print
        print('Buliding issue repository')
        try:
            for commit in all_commits:
                commits_scanned += 1

                # prints the progress
                print_commit_progress(datetime.now(), start)

                # finds all the issues in the commit
                result = repotool.find_pattern_in_tree(
                    commit.tree, pattern, commit.hexsha)
                all_matches.extend(result)
        except KeyboardInterrupt:
            print(' ')
            print('Setup issue repository process interupted')
            print('Cleaning up')
            reset_issue_repo()
            print('Done')
            sys.exit(0)
    else:
        print('Curent repository is empty')
        return

    return


def init(args):

    if args.reset:
        reset_issue_repo()

    if not system.is_init():
        setup_folders()

        if system.yes_no_option('Build issue repository from past commits'):
            build_from_past_commits()
    else:
        print('Issue repository already setup')

    return
