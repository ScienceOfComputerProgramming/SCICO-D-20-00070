import sys
import os
import shutil
from unittest import TestCase
from unittest.mock import patch
from gitissue import IssueRepo, IssueTree


class TestCreateIssueTree(TestCase):

    data = None
    repo = None
    issue_sha = None

    @classmethod
    def setUpClass(cls):
        os.makedirs('here')
        os.makedirs('here/objects')

        cls.data = [{'filepath': '.gitignore', 'issues':
                     ['the contents of the file', 'another issue', 'yet another issue']},
                    {'filepath': 'file.yaml', 'issues':
                     ['the contents of the file', 'another issue', 'yet another issue']}
                    ]
        cls.repo = IssueRepo()
        cls.repo.issue_dir = 'here'
        cls.repo.issue_objects_dir = 'here/objects'

    def test1_create_issue_tree(self):
        itree = IssueTree.create(self.repo, self.data)
        self.assertEqual(len(itree.issues), 6)
        TestCreateIssueTree.issue_sha = (itree.binsha, itree.hexsha)

    def test2_get_issue_tree_binsha(self):
        itree = IssueTree(self.repo, TestCreateIssueTree.issue_sha[0])
        self.assertEqual(len(itree.issues), 6)

    def test2_get_issue_tree_hexsha(self):
        itree = IssueTree(self.repo, TestCreateIssueTree.issue_sha[1])
        self.assertEqual(len(itree.issues), 6)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree('here')
