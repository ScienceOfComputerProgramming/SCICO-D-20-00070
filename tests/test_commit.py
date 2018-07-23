import os
import shutil
from unittest import TestCase

from git import Tree, Repo
from sciit import Issue, IssueRepo, IssueTree, IssueCommit

from tests.external_resources import safe_create_repo_dir


class TestCreateIssueCommit(TestCase):

    repo = None
    issue_tree = None
    gitcommit = None

    @classmethod
    def setUpClass(cls):
        safe_create_repo_dir('here')

        data = [{'id': '1', 'title': 'the contents of the file'},
                {'id': '2', 'title': 'the contents of the file'},
                {'id': '3', 'title': 'the contents of the file'},
                {'id': '4', 'title': 'the contents of the file'},
                {'id': '5', 'title': 'the contents of the file'},
                {'id': '6', 'title': 'the contents of the file'}]
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
        self.assertEqual(self.gitcommit.binsha, icommit.binsha)
        self.assertEqual(len(icommit.issuetree.issues), 6)
        self.assertEqual(icommit.open_issues, 6)
