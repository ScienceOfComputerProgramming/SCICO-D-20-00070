from unittest import TestCase

from sciit import Issue, IssueRepo
from tests.external_resources import safe_create_repo_dir


class TestIssue(TestCase):

    @classmethod
    def setUpClass(cls):

        cls.data = {'id': '1',
                    'title': 'new issue here',
                    'filepath': '.gitignore',
                    'contents': '# Adding a new thing\nAuthor: someone on the team'}
        cls.data1 = {'id': '2',
                     'title': 'new issue here2',
                     'filepath': '.gitignore',
                     'contents': '# something different'}
        cls.data3 = {'id': '2',
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
        cls.repo = IssueRepo(issue_dir='here')
        cls.issue = Issue.create(cls.repo, cls.data.copy())
        cls.issue1 = Issue.create(cls.repo, cls.data1.copy())

    def test_create_issue(self):
        issue = Issue.create(self.repo, self.data.copy())
        self.assertTrue(issue.size > 0)
        self.assertNotEqual(self.data, issue.data)
        self.assertIn(self.data['filepath'], issue.data['filepath'])
        self.assertIn(self.data['contents'], issue.data['contents'])

    def test_create_existing_issue_returns_existing_issue(self):
        issue = Issue.create(self.repo, TestIssue.data)
        self.assertEqual(self.issue, issue)

    def test_retreive_issue_binsha(self):
        binsha = self.issue.binsha
        issue = Issue(self.repo, binsha)
        self.assertEqual(self.issue, issue)

    def test_retreive_issue_hexsha(self):
        hexsha = self.issue.hexsha
        issue = Issue(self.repo, hexsha)
        self.assertEqual(self.issue, issue)

    def test_create_separate_issues_from_similar_content(self):
        issue = Issue.create(self.repo, self.data1.copy())
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
        issue = Issue.create(self.repo, self.data3.copy())
        self.assertTrue(hasattr(issue, 'id'))
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
        issue = Issue.create(self.repo, self.data3.copy())
        issue = Issue(self.repo, issue.binsha)
        self.assertTrue(hasattr(issue, 'id'))
        self.assertTrue(hasattr(issue, 'title'))
        self.assertTrue(hasattr(issue, 'description'))
        self.assertTrue(hasattr(issue, 'assignees'))
        self.assertTrue(hasattr(issue, 'due_date'))
        self.assertTrue(hasattr(issue, 'label'))
        self.assertTrue(hasattr(issue, 'weight'))
        self.assertTrue(hasattr(issue, 'priority'))
        self.assertTrue(hasattr(issue, 'filepath'))
        self.assertTrue(hasattr(issue, 'size'))


