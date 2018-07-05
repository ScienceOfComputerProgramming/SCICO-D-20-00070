import os
import shutil
from unittest import TestCase

from git import Tree, Repo
from gitissue import Issue, IssueRepo, IssueTree, IssueCommit


class TestCreateIssueCommit(TestCase):

    repo = None
    issue_tree = None
    gitcommit = None

    @classmethod
    def setUpClass(cls):
        os.makedirs('here')
        os.makedirs('here/objects')

        data = [{'number': '1', 'description': 'the contents of the file'},
                {'number': '2', 'description': 'the contents of the file'},
                {'number': '3', 'description': 'the contents of the file'},
                {'number': '4', 'description': 'the contents of the file'},
                {'number': '5', 'description': 'the contents of the file'},
                {'number': '6', 'description': 'the contents of the file'}]
        cls.repo = IssueRepo()
        cls.repo.issue_dir = 'here'
        cls.repo.issue_objects_dir = 'here/objects'
        issues = []
        for issue_data in data:
            issues.append(Issue.create(cls.repo, issue_data))
        cls.issue_tree = IssueTree.create(cls.repo, issues)
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
