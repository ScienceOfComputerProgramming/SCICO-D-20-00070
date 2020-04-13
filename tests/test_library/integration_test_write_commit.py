import unittest

import logging
import os

from git import Repo as GitRepository

from tests.external_resources import remove_existing_repo

from sciit import IssueRepo
from sciit.write_commit import create_issue, update_issue, close_issue


class IntegrationTestWriteCommit(unittest.TestCase):

    def test_sequence(self):

        remove_existing_repo('./working_dir')
        os.mkdir("./working_dir")
        os.chdir("./working_dir")

        git_repository = GitRepository.init(".")

        with (open("README.md", 'w')) as readme_file_handle:
            readme_file_handle.write("We're going on a bear hunt, by Michael Rosen\n")

        git_repository.index.add(["README.md"])
        git_repository.index.commit("Initial commit")
        git_repository.git.checkout("README.md")

        issue_repository = IssueRepo(git_repository)
        issue_repository.setup_file_system_resources()
        issue_repository.cache_issue_snapshots_from_all_commits()

        issue_id = create_issue(issue_repository, '''We're going on a bear hunt.''')
        issues = issue_repository.get_all_issues()
        issue = issues[issue_id]

        changes = {'title': '''We're going to catch a big one.'''}

        update_issue(issue_repository, issue, changes)

        close_issue(issue_repository, issue)

        logging.info("Closed issue.")

        # Forces proper clean up of git repository resources on Windows.
        # See https://github.com/gitpython-developers/GitPython/issues/508
        git_repository.__del__()

        os.chdir('../')
        remove_existing_repo('./working_dir')


if __name__ == '__main__':
    unittest.main()
