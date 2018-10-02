from unittest import TestCase

from sciit import IssueSnapshot, IssueRepo
from tests.external_resources import safe_create_repo_dir


class TestIssue(TestCase):

    def setUp(self):

        self.data = {'issue_id': '1',
                    'title': 'new issue here',
                    'filepath': '.gitignore',
                    'contents': '# Adding a new thing\nAuthor: someone on the team'}
        self.data1 = {'issue_id': '2',
                     'title': 'new issue here2',
                     'filepath': '.gitignore',
                     'contents': '# something different'}
        self.data3 = {'issue_id': '2',
                     'title': 'The title of your issue',
                     'description': 'A description of you issue as you\n'
                     + 'want it to be ``markdown`` supported',
                     'assignees': 'nystrome, kevin, daniels',
                     'due_date': '12 oct 2018',
                     'label': 'in-development',
                     'weight': '4',
                     'priority': 'high',
                     'filepath': 'README.md'}

        safe_create_repo_dir('here')
        self.repo = IssueRepo(issue_dir='here')

        self.issue = IssueSnapshot.create_from_data(self.repo, self.data.copy())
        self.issue1 = IssueSnapshot.create_from_data(self.repo, self.data1.copy())

    def test_create_issue(self):
        issue = IssueSnapshot.create_from_data(self.repo, self.data.copy())
        self.assertTrue(issue.size > 0)
        self.assertNotEqual(self.data, issue.data)
        self.assertIn(self.data['filepath'], issue.data['filepath'])
        self.assertIn(self.data['contents'], issue.data['contents'])

    def test_create_existing_issue_returns_existing_issue(self):
        issue = IssueSnapshot.create_from_data(self.repo, self.data)
        self.assertEqual(self.issue, issue)

    def test_retreive_issue_binsha(self):
        binsha = self.issue.binsha

        issue = IssueSnapshot.create_from_binsha(self.repo, binsha)
        self.assertEqual(self.issue, issue)

    def test_retreive_issue_hexsha(self):
        hexsha = self.issue.hexsha
        issue = IssueSnapshot.create_from_hexsha(self.repo, hexsha)
        self.assertEqual(self.issue, issue)

    def test_create_separate_issues_from_similar_content(self):
        issue = IssueSnapshot.create_from_data(self.repo, self.data1.copy())
        self.assertTrue(issue.size > 0)
        self.assertNotEqual(self.data1, issue.data)
        self.assertIn(self.data1['filepath'], issue.data['filepath'])
        self.assertIn(self.data1['contents'], issue.data['contents'])
        self.assertNotEqual(self.issue, issue)

    def test_second_issue_created_gt_first(self):
        self.assertGreater(self.issue1, self.issue)

    def test_first_issue_created_lt_second(self):
        self.assertLess(self.issue, self.issue1)

    def test_issue_string_printed_properly(self):
        self.assertTrue('Issue#' in str(self.issue))

    def test_create_issue_full_metadata(self):
        issue = IssueSnapshot.create_from_data(self.repo, self.data3.copy())
        self.assertTrue(hasattr(issue, 'issue_id'))
        self.assertTrue(hasattr(issue, 'title'))
        self.assertTrue(hasattr(issue, 'description'))
        self.assertTrue(hasattr(issue, 'assignees'))
        self.assertTrue(hasattr(issue, 'due_date'))
        self.assertTrue(hasattr(issue, 'label'))
        self.assertTrue(hasattr(issue, 'weight'))
        self.assertTrue(hasattr(issue, 'priority'))
        self.assertTrue(hasattr(issue, 'filepath'))
        self.assertTrue(hasattr(issue, 'size'))

    def test_get_issue_full_metadata(self):
        issue = IssueSnapshot.create_from_data(self.repo, self.data3.copy())
        issue = IssueSnapshot.create_from_binsha(self.repo, issue.binsha)
        self.assertTrue(hasattr(issue, 'issue_id'))
        self.assertTrue(hasattr(issue, 'title'))
        self.assertTrue(hasattr(issue, 'description'))
        self.assertTrue(hasattr(issue, 'assignees'))
        self.assertTrue(hasattr(issue, 'due_date'))
        self.assertTrue(hasattr(issue, 'label'))
        self.assertTrue(hasattr(issue, 'weight'))
        self.assertTrue(hasattr(issue, 'priority'))
        self.assertTrue(hasattr(issue, 'filepath'))
        self.assertTrue(hasattr(issue, 'size'))


