import sys
import os
import shutil
from unittest import TestCase
from unittest.mock import patch
from gitissue import IssueRepo, IssueTree, IssueCommit


class TestCreateIssueCommit(TestCase):

    repo = None
    issue_tree = None
    gitcommit = None

    @classmethod
    def setUpClass(cls):
        os.makedirs('here')
        os.makedirs('here/objects')

        data = [{'filepath': '.gitignore', 'issues':
                 ['the contents of the file', 'another issue', 'yet another issue']},
                {'filepath': 'file.yaml', 'issues':
                 ['the contents of the file', 'another issue', 'yet another issue']}
                ]
        cls.repo = IssueRepo()
        cls.repo.issue_dir = 'here'
        cls.repo.issue_objects_dir = 'here/objects'
        cls.issue_tree = IssueTree.create(cls.repo, data)
        cls.gitcommit = cls.repo.head.commit

    def test1_create_issue_commit(self):
        icommit = IssueCommit.create(
            self.repo, self.gitcommit, self.issue_tree)
        self.assertEqual(self.gitcommit.hexsha, icommit.hexsha)
        self.assertEqual(len(icommit.issuetree.issues), 6)
        self.assertEqual(self.gitcommit.hexsha, icommit.commit.hexsha)

    def test2_get_issue_commit_hexsha(self):
        icommit = IssueCommit(self.repo, self.gitcommit.hexsha)
        self.assertEqual(self.gitcommit.hexsha, icommit.hexsha)
        self.assertEqual(len(icommit.issuetree.issues), 6)
        self.assertEqual(self.gitcommit.hexsha, icommit.commit.hexsha)

    def test3_get_issue_commit_binsha(self):
        icommit = IssueCommit(self.repo, self.gitcommit.binsha)
        self.assertEqual(self.gitcommit.hexsha, icommit.hexsha)
        self.assertEqual(len(icommit.issuetree.issues), 6)
        self.assertEqual(self.gitcommit.hexsha, icommit.commit.hexsha)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree('here')
