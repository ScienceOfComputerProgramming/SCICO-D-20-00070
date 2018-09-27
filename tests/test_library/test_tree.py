from unittest import TestCase
from sciit import IssueRepo, IssueTree, Issue
from tests.external_resources import safe_create_repo_dir


class TestCreateIssueTree(TestCase):

    def setUp(self):
        safe_create_repo_dir('here')

        data = [{'id': '1', 'title': 'the contents of the file'},
                {'id': '2', 'title': 'the contents of the file'},
                {'id': '3', 'title': 'the contents of the file'},
                {'id': '4', 'title': 'the contents of the file'},
                {'id': '5', 'title': 'the contents of the file'},
                {'id': '6', 'title': 'the contents of the file'}]
        self.repo = IssueRepo()
        self.repo.issue_dir = 'here'
        self.repo.issue_objects_dir = 'here/objects'
        self.issues = []
        for issue_data in data:
            self.issues.append(Issue.create_from_data(self.repo, issue_data))

    def test_create_issue_tree(self):
        itree = IssueTree.create(self.repo, self.issues)
        self.assertEqual(len(itree.issues), 6)
        TestCreateIssueTree.issue_sha = (itree.binsha, itree.hexsha)

    def test_get_issue_tree_binsha(self):
        itree = IssueTree.create(self.repo, self.issues)
        itree = IssueTree(self.repo, itree.hexsha)
        itree = IssueTree(self.repo, itree.binsha)
        self.assertEqual(len(itree.issues), 6)
