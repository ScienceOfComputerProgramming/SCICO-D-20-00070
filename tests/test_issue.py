"""
This module tests the functionality of the functions module.
"""
import sys
import os
import shutil
from unittest import TestCase
from unittest.mock import patch
from gitissue import Issue, IssueRepo
from gitissue.issue import get_new_issue_no


class TestRepo():
    def __init__(self, issue_dir):
        super(TestRepo, self).__init__()
        self.issue_dir = issue_dir


class TestGetNewIssueNumber(TestCase):

    @classmethod
    def setUpClass(cls):
        os.makedirs('here')

    def setUp(self):
        self.repo = TestRepo('here')

    def test1_creates_new_issue_number_file(self):
        number = get_new_issue_no(self.repo)
        self.assertEqual(number, 1)
        self.assertTrue(os.path.exists('here/NUMBER'))

    def test2_get_incremented_issue_number(self):
        number = get_new_issue_no(self.repo)
        self.assertEqual(number, 2)
        self.assertTrue(os.path.exists('here/NUMBER'))

    def test3_get_incremented_number(self):
        f = open('here/NUMBER', 'w')
        f.write('23')
        f.close()
        number = get_new_issue_no(self.repo)
        self.assertEqual(number, 24)
        self.assertTrue(os.path.exists('here/NUMBER'))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree('here')


class TestIssue(TestCase):

    data = {'number': '1',
            'filepath': '.gitignore',
            'contents': '# Adding a new thing\nAuthor: someone on the team'}
    data1 = {'number': '2',
             'filepath': '.gitignore',
             'contents': '# something different'}
    repo = None
    issue = None
    issue2 = None

    @classmethod
    def setUpClass(cls):
        os.makedirs('here')
        os.makedirs('here/objects')
        cls.repo = IssueRepo()
        cls.repo.issue_dir = 'here'
        cls.repo.issue_objects_dir = 'here/objects'

    def test1_create_issue(self):
        issue = Issue.create(self.repo, TestIssue.data.copy())
        self.assertTrue(issue.size > 0)
        self.assertEqual(TestIssue.data, issue.data)
        self.assertIn(TestIssue.data['filepath'], issue.data['filepath'])
        self.assertIn(TestIssue.data['contents'], issue.data['contents'])
        TestIssue.issue = issue

    def test2_create_existing_issue_returns_existing_issue(self):
        issue = Issue.create(self.repo, TestIssue.data)
        self.assertEqual(TestIssue.issue, issue)

    def test3_retreive_issue_binsha(self):
        binsha = TestIssue.issue.binsha
        issue = Issue(self.repo, binsha)
        self.assertEqual(TestIssue.issue, issue)

    def test4_retreive_issue_hexsha(self):
        hexsha = TestIssue.issue.hexsha
        issue = Issue(self.repo, hexsha)
        self.assertEqual(TestIssue.issue, issue)

    def test5_create_separate_issues_from_similar_content(self):
        issue = Issue.create(self.repo, TestIssue.data1.copy())
        self.assertTrue(issue.size > 0)
        self.assertEqual(TestIssue.data1, issue.data)
        self.assertIn(TestIssue.data1['filepath'], issue.data['filepath'])
        self.assertIn(TestIssue.data1['contents'], issue.data['contents'])
        self.assertNotEqual(TestIssue.issue, issue)
        TestIssue.issue2 = issue

    def test6_second_issue_created_gt_first(self):
        self.assertGreater(TestIssue.issue2, TestIssue.issue)

    def test6_first_issue_created_lt_second(self):
        self.assertLess(TestIssue.issue, TestIssue.issue2)

    def test7_issue_string_printed_properly(self):
        self.assertTrue('Issue#1 ' in str(TestIssue.issue))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree('here')
