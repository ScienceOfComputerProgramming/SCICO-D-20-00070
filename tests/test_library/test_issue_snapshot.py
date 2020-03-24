from unittest import TestCase

from unittest.mock import MagicMock

from sciit import IssueSnapshot
from tests.external_resources import safe_create_repo_dir


class TestIssueSnapshot(TestCase):

    def setUp(self):

        self.data = {
            'issue_id': '1',
            'title': 'new issue here',
            'file_path': '.gitignore',
            'contents': '# Adding a new thing\nAuthor: someone on the team'}
        self.data1 = {
            'issue_id': '2',
            'title': 'new issue here2',
            'file_path': '.gitignore',
            'contents': '# something different'}
        self.data3 = {
            'issue_id': '2',
            'title': 'The title of your issue',
            'description': 'A description of you issue as you\nwant it to be ``markdown`` supported',
            'assignees': 'nystrome, kevin, daniels',
            'due_date': '12 oct 2018',
            'labels': 'in-development',
            'weight': '4',
            'priority': 'high',
            'file_path': 'README.md'}

        safe_create_repo_dir('here')

        self.commit = MagicMock()

        self.issue_snapshot_1 = IssueSnapshot(self.commit, self.data.copy(), ['master'])
        self.issue_snapshot_2 = IssueSnapshot(self.commit, self.data1.copy(), ['master'])

    def test_create_issue_snapshot(self):
        issue_snapshot = IssueSnapshot(self.commit, self.data.copy(), ['master'])
        self.assertIn(self.data['file_path'], issue_snapshot.data['file_path'])
        self.assertIn(self.data['contents'], issue_snapshot.data['contents'])

    def test_create_existing_issue_snapshot_returns_existing_issue(self):
        issue = IssueSnapshot(self.commit, self.data, ['master'])
        self.assertEqual(self.issue_snapshot_1, issue)

    def test_second_issue_created_gt_first(self):
        self.assertGreater(self.issue_snapshot_2, self.issue_snapshot_1)

    def test_first_issue_created_lt_second(self):
        self.assertLess(self.issue_snapshot_1, self.issue_snapshot_2)

    def test_issue_string_printed_properly(self):
        self.assertTrue('@' in str(self.issue_snapshot_1))

    def test_create_issue_snapshot_full_metadata(self):
        issue_snapshot = IssueSnapshot(self.commit, self.data3.copy(), ['master'])
        self.assertTrue(hasattr(issue_snapshot, 'issue_id'))
        self.assertTrue(hasattr(issue_snapshot, 'title'))
        self.assertTrue(hasattr(issue_snapshot, 'description'))
        self.assertTrue(hasattr(issue_snapshot, 'assignees'))
        self.assertTrue(hasattr(issue_snapshot, 'due_date'))
        self.assertTrue(hasattr(issue_snapshot, 'labels'))
        self.assertTrue(hasattr(issue_snapshot, 'weight'))
        self.assertTrue(hasattr(issue_snapshot, 'priority'))
        self.assertTrue(hasattr(issue_snapshot, 'file_path'))

    def test_get_issue_snapshot_full_metadata(self):
        issue_snapshot = IssueSnapshot(self.commit, self.data3.copy(), ['master'])
        self.assertTrue(hasattr(issue_snapshot, 'issue_id'))
        self.assertTrue(hasattr(issue_snapshot, 'title'))
        self.assertTrue(hasattr(issue_snapshot, 'description'))
        self.assertTrue(hasattr(issue_snapshot, 'assignees'))
        self.assertTrue(hasattr(issue_snapshot, 'due_date'))
        self.assertTrue(hasattr(issue_snapshot, 'labels'))
        self.assertTrue(hasattr(issue_snapshot, 'weight'))
        self.assertTrue(hasattr(issue_snapshot, 'priority'))
        self.assertTrue(hasattr(issue_snapshot, 'file_path'))


