import sys
import os
import shutil
from unittest import TestCase
from unittest.mock import patch
from gitissue import IssueRepo
from gitissue.errors import EmptyRepositoryError


class TestIssueRepo(TestCase):

    def test_issue_repo_is_init(self):
        if not os.path.exists('here'):
            os.makedirs('here')
            os.makedirs('here/objects')
        repo = IssueRepo()
        repo.issue_dir = 'here'
        repo.issue_objects_dir = 'here/objects'
        self.assertTrue(repo.is_init())

    def test_issue_repo_is_not_init(self):
        repo = IssueRepo()
        repo.issue_dir = 'here'
        repo.issue_objects_dir = 'here/objects'
        self.assertFalse(repo.is_init())

    def test_reset_init_repo(self):
        if not os.path.exists('here'):
            os.makedirs('here')
            os.makedirs('here/objects')
        repo = IssueRepo()
        repo.issue_dir = 'here'
        repo.issue_objects_dir = 'here/objects'
        repo.reset()
        self.assertFalse(os.path.exists('here'))

    def test_reset_non_init_repo(self):
        repo = IssueRepo()
        repo.issue_dir = 'here'
        repo.issue_objects_dir = 'here/objects'
        with self.assertRaises(EmptyRepositoryError) as context:
            repo.reset()
        self.assertTrue(
            'The issue repository is empty.' in str(context.exception))

    def test_repo_setup_correctly(self):
        repo = IssueRepo()
        repo.issue_dir = 'here'
        repo.issue_objects_dir = 'here/objects'
        repo.setup()
        self.assertTrue(os.path.exists('here'))
        self.assertTrue(os.path.exists('here/objects'))

    def tearDown(self):
        if os.path.exists('here'):
            shutil.rmtree('here')
