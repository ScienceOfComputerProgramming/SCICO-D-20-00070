"""
This module tests the functionality of the functions module.
"""
import sys
import os
import shutil
from unittest import TestCase
from unittest.mock import patch
from gitissue import Issue, IssueRepo
from gitissue.issue import find_issue_data_in_comment


class TestIssue(TestCase):

    data = {'number': '1',
            'filepath': '.gitignore',
            'contents': '# Adding a new thing\nAuthor: someone on the team'}
    data1 = {'number': '2',
             'filepath': '.gitignore',
             'contents': '# something different'}
    data3 = {'number': '2',
             'title': 'The title of your issue',
             'description': 'A description of you issue as you\n'
             + 'want it to be ``markdown`` supported',
             'assignees': 'nystrome, kevin, daniels',
             'due_date': '12 oct 2018',
             'label': 'in-development',
             'weight': '4',
             'priority': 'high',
             'filepath': 'README.md'}

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

    def test7_first_issue_created_lt_second(self):
        self.assertLess(TestIssue.issue, TestIssue.issue2)

    def test8_issue_string_printed_properly(self):
        self.assertTrue('Issue#1 ' in str(TestIssue.issue))

    def test90_create_issue_full_metadata(self):
        issue = Issue.create(self.repo, TestIssue.data3.copy())
        self.assertTrue(hasattr(issue, 'number'))
        self.assertTrue(hasattr(issue, 'title'))
        self.assertTrue(hasattr(issue, 'description'))
        self.assertTrue(hasattr(issue, 'assignees'))
        self.assertTrue(hasattr(issue, 'due_date'))
        self.assertTrue(hasattr(issue, 'label'))
        self.assertTrue(hasattr(issue, 'weight'))
        self.assertTrue(hasattr(issue, 'priority'))
        self.assertTrue(hasattr(issue, 'filepath'))
        TestIssue.issue = issue

    def test91_get_issue_full_metadata(self):
        issue = Issue(self.repo, TestIssue.issue.hexsha)
        self.assertTrue(hasattr(issue, 'number'))
        self.assertTrue(hasattr(issue, 'title'))
        self.assertTrue(hasattr(issue, 'description'))
        self.assertTrue(hasattr(issue, 'assignees'))
        self.assertTrue(hasattr(issue, 'due_date'))
        self.assertTrue(hasattr(issue, 'label'))
        self.assertTrue(hasattr(issue, 'weight'))
        self.assertTrue(hasattr(issue, 'priority'))
        self.assertTrue(hasattr(issue, 'filepath'))
        self.assertTrue(hasattr(issue, 'size'))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree('here')


class TestFindIssueInComment(TestCase):

    def test_no_issue_data_if_number_not_specified(self):
        comment = """
        @description here is a description of the item
        """
        data = find_issue_data_in_comment(comment)
        self.assertEqual(data, {})

    def test_find_number_only(self):
        comment = """
        @issue 2
        """
        data = find_issue_data_in_comment(comment)
        self.assertIn('number', data)
        self.assertEqual(data['number'], '2')

    def test_find_number_and_title(self):
        comment = """
        @issue 2
        @title something new
        """
        data = find_issue_data_in_comment(comment)
        self.assertIn('number', data)
        self.assertEqual(data['number'], '2')
        self.assertIn('title', data)
        self.assertEqual(data['title'], 'something new')

    def test_find_number_and_description_inline(self):
        comment = """
        @issue 2
        @description something will be found
        """
        data = find_issue_data_in_comment(comment)
        self.assertIn('number', data)
        self.assertEqual(data['number'], '2')
        self.assertIn('description', data)
        self.assertIn('something will be found', data['description'])

    def test_find_number_and_description_newline(self):
        comment = """
        @issue 2
        @description 
                something will be found
        """
        data = find_issue_data_in_comment(comment)
        self.assertIn('number', data)
        self.assertEqual(data['number'], '2')
        self.assertIn('description', data)
        self.assertIn('something will be found', data['description'])

    def test_find_number_and_description_between_metadata(self):
        comment = """
        @issue 2
        @description 
            something will be found
        @due_date today
        """
        data = find_issue_data_in_comment(comment)
        self.assertIn('number', data)
        self.assertEqual(data['number'], '2')
        self.assertIn('description', data)
        self.assertIn('something will be found', data['description'])

    def test_find_number_and_assignees(self):
        comment = """
        @issue 2
        @assignees mark, peter, paul
        """
        data = find_issue_data_in_comment(comment)
        self.assertIn('number', data)
        self.assertEqual(data['number'], '2')
        self.assertIn('assignees', data)
        self.assertEqual(data['assignees'], 'mark, peter, paul')

    def test_find_number_and_due_date(self):
        comment = """
        @issue 2
        @due_date 10 dec 2018
        """
        data = find_issue_data_in_comment(comment)
        self.assertIn('number', data)
        self.assertEqual(data['number'], '2')
        self.assertIn('due_date', data)
        self.assertEqual(data['due_date'], '10 dec 2018')

    def test_find_number_and_label(self):
        comment = """
        @issue 2
        @label in-development, main-feature
        """
        data = find_issue_data_in_comment(comment)
        self.assertIn('number', data)
        self.assertEqual(data['number'], '2')
        self.assertIn('label', data)
        self.assertEqual(data['label'], 'in-development, main-feature')

    def test_find_number_and_weight(self):
        comment = """
        @issue 2
        @weight 7
        """
        data = find_issue_data_in_comment(comment)
        self.assertIn('number', data)
        self.assertEqual(data['number'], '2')
        self.assertIn('weight', data)
        self.assertEqual(data['weight'], '7')

    def test_find_number_and_priority(self):
        comment = """
        @issue 2
        @priority mid-high
        """
        data = find_issue_data_in_comment(comment)
        self.assertIn('number', data)
        self.assertEqual(data['number'], '2')
        self.assertIn('priority', data)
        self.assertEqual(data['priority'], 'mid-high')

    def test_find_all_metadata(self):
        comment = """
        @issue #2
        @title The title of your issue
        @description:
            A description of you issue as you
            want it to be ``markdown`` supported
        @assignees nystrome, kevin, daniels
        @due date 12 oct 2018
        @label in-development
        @weight 4
        @priority high
        """
        data = find_issue_data_in_comment(comment)
        self.assertIn('number', data)
        self.assertEqual(data['number'], '2')
        self.assertIn('title', data)
        self.assertEqual(data['title'], 'The title of your issue')
        self.assertIn('description', data)
        self.assertIn('of you issue as you\n', data['description'])
        self.assertIn('assignees', data)
        self.assertEqual(data['assignees'], 'nystrome, kevin, daniels')
        self.assertIn('due_date', data)
        self.assertEqual(data['due_date'], '12 oct 2018')
        self.assertIn('label', data)
        self.assertEqual(data['label'], 'in-development')
        self.assertIn('weight', data)
        self.assertEqual(data['weight'], '4')
        self.assertIn('priority', data)
        self.assertEqual(data['priority'], 'high')
