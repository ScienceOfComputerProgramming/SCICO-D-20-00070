import os
from git import Repo
from gitissue.tools import system

repo = Repo()


def setup_folders():
    print('Setting up folders...')
    issue_dir = repo.git_dir + '/issue'
    issue_objects_dir = issue_dir + '/objects'
    os.makedirs(issue_dir)
    os.makedirs(issue_objects_dir)


def build_from_past_commits():
    # from collections import Counter
    import re
    import sys
    from datetime import datetime

    start = datetime.now()
    commits_scanned = 0

    # initialize to the current repo
    issue_directory = repo.working_dir + '/.git/issue'
    pattern = r'(^\s*#.*$)'
    pattern = re.compile(pattern, re.MULTILINE)
    all_matches = []

    def read_tree(tree, commit_sha):
        try:
            for item in tree:
                if item.type == 'blob':
                    # show read the data contained in that file
                    try:
                        object_contents = item.data_stream.read().decode('utf-8')
                        matched_issues = pattern.findall(object_contents)
                        # print(object_contents)
                        if matched_issues is not None:
                            matches.extend(matched_issues)
                            all_matches.extend(matched_issues)
                            print
                            print('**********')
                            print(item.path)
                            print
                            for match in matched_issues:
                                print(match)
                    except UnicodeDecodeError:
                        pass
                else:
                    read_tree(item, commit_sha)
        except:
            pass


    # if the repo is not empty
    if not repo.bare:
        try:
            # get all commits on the master branch
            all_commits = list(repo.iter_commits('master'))

            for commit in all_commits:
                commits_scanned += 1
                matches = []
                # show the commits that we received
                print('commit ' + str(commit))

                # this gets all the filenames relative to the
                # working directory
                # print(commit.stats.files.keys())
                # print(commit.data_stream.read().decode('utf-8'))

                read_tree(commit.tree, commit.hexsha)
                print(matches)
        except KeyboardInterrupt:
            stored_exc = sys.exc_info()
    else:
        print('Curent repository is empty')
        return

    done = datetime.now()
    duration = done - start
    print('duration: ' + str(duration))
    print('commits: ' + str(len(all_commits)))
    return


def init(args):

    if system.yes_no_option('Do you want setup your issue repository'):

        if not system.is_init():
            setup_folders()

            if system.yes_no_option('Build issue repository from past commits'):
                build_from_past_commits()
        else:
            print('Issue repository already setup')
        # remotes = repo.remotes
        # if not remotes:
        #     print('error')
        # else:
        #     print(remotes)

    return
