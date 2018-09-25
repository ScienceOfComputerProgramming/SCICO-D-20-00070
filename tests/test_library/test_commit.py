import random
import string
from unittest import TestCase
from unittest.mock import Mock, patch, mock_open

from git import Commit
from git.util import hex_to_bin
from sciit import Issue, IssueCommit, IssueRepo, IssueTree
from sciit.commit import find_issues_in_commit, find_issue_data_in_comment
from sciit.functions import write_last_issue, get_sciit_ignore
from tests.external_resources import safe_create_repo_dir

pattern = r'((?:#.*(?:\n\s*#)*.*)|(?:#.*)|(?:#.*$))'


def random_40_chars():
    return [random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(40)]


class TestCreateIssueCommit(TestCase):

    @classmethod
    def setUpClass(cls):
        safe_create_repo_dir('here')

        cls.repo = IssueRepo('here')

        data = [{'id': '1', 'title': 'the contents of the file', 'filepath': 'path',
                 'description': 'This issue had a description'},
                {'id': '2', 'title': 'the contents of the file', 'filepath': 'path'},
                {'id': '3', 'title': 'the contents of the file', 'filepath': 'path'},
                {'id': '4', 'title': 'the contents of the file', 'filepath': 'path'},
                {'id': '5', 'title': 'the contents of the file', 'filepath': 'path'},
                {'id': '6',
                 'title': 'The title of your issue',
                 'description': 'A description of you issue as you\n'
                 + 'want it to be ``markdown`` supported',
                 'assignees': 'nystrome, kevin, daniels',
                 'due_date': '12 oct 2018',
                 'label': 'in-development',
                 'weight': '4',
                 'priority': 'high',
                 'filepath': 'README.md'}]

        new_data = [{'id': '1', 'title': 'the contents of the file', 'filepath': 'path'},
                    {'id': '2', 'title': 'the contents of the file', 'filepath': 'path'},
                    {'id': '9', 'title': 'the contents of the file', 'filepath': 'path'},
                    {'id': '6', 'title': 'the contents of the file', 'filepath': 'path',
                     'description': 'description has changed'},
                    {'id': '12', 'title': 'the contents of the file', 'filepath': 'path',
                     'description': 'here is a nice description'}]

        cls.issues = list()
        cls.new_issues = list()

        for d in data:
            cls.issues.append(Issue.create(cls.repo, d))
        cls.itree = IssueTree.create(cls.repo, cls.issues)

        for d in new_data:
            cls.new_issues.append(Issue.create(cls.repo, d))

        cls.new_itree = IssueTree.create(cls.repo, cls.new_issues)

        cls.second = '622918a4c6539f853320e06804f73d1165df69d0'
        cls.first = '43e8d11ec2cb9802151533ae8d9c5dcc5dec91a4'
        cls.second_commit = Commit(cls.repo, hex_to_bin(cls.second))
        cls.first_commit = Commit(cls.repo, hex_to_bin(cls.first))
        cls.second_icommit = IssueCommit.create(cls.repo, cls.second_commit, cls.new_itree)
        cls.first_icommit = IssueCommit.create(cls.repo, cls.first_commit, cls.itree)

        write_last_issue(cls.repo.issue_dir, cls.second)

    def test_create_issue_commit(self):
        icommit = IssueCommit.create(
            self.repo, self.first_commit, self.itree)

        self.assertEqual(self.first_commit.hexsha, icommit.hexsha)
        self.assertEqual(self.first_commit.binsha, icommit.binsha)
        self.assertEqual(len(icommit.issuetree.issues), 6)
        self.assertEqual(icommit.open_issues, 6)


class FindIssuesInCommit(TestCase):

    def setUp(self):
        safe_create_repo_dir('here')
        self.repo = IssueRepo()
        self.repo.issue_dir = 'here'
        self.repo.issue_objects_dir = 'here/objects'

    def commit_mock(self, trees=list(), blobs=list(), commit_files=None):
        commit = Mock()
        commit.tree = self.tree_mock(trees, blobs)
        if not commit_files:
            commit_files = [blob.path for blob in commit.tree.blobs]
        commit.stats.files.keys.return_value = commit_files
        commit.parents = list()
        return commit

    def tree_mock(self, trees=list(), blobs=list()):
        tree = Mock()
        tree.trees = trees
        tree.blobs = blobs
        return tree

    def blob_mock(self, content=None, mime_type=None, path=None):
        blob = Mock()
        blob.path = path
        blob.type = 'blob'
        blob.mime_type = mime_type
        blob.data_stream = Mock()
        blob.data_stream.read = Mock(return_value=content)
        return blob

    def test_no_issues_one_changed_file(self):
        commit = self.commit_mock(
            blobs=[
                self.blob_mock(
                    content=b'value that has some contents',
                    mime_type='text',
                    path='README')
            ])

        issues = find_issues_in_commit(self.repo, commit, pattern)
        self.assertFalse(issues)

    def test_one_cstyle_issue_cleaned(self):
        commit = self.commit_mock(
            blobs=[
                self.blob_mock(
                    content=b'/*@issue 2\n* @description \n * value that has some contents\n*/',
                    mime_type='text/x-java',
                    path='hello.java')
            ]
        )

        issues = find_issues_in_commit(self.repo, commit)
        self.assertEqual(len(issues), 1)
        self.assertNotIn('*', issues[0].description)

    def test_one_hashstyle_issue_cleaned(self):
        commit = self.commit_mock(
            blobs=[
                self.blob_mock(
                    content=b'#***\n#@issue 2\n# @description \n # value that has some contents\n#***',
                    mime_type='text/plain',
                    path='hello')
            ]
        )

        issues = find_issues_in_commit(self.repo, commit)
        self.assertEqual(len(issues), 1)
        self.assertNotIn('#', issues[0].description)

    def test_one_markdown_issue_cleaned(self):
        commit = self.commit_mock(
            blobs=[
                self.blob_mock(
                    content=
                    b"""
---
@issue 2
@description 
value that has some contents
---
                    """,
                    mime_type='text/plain',
                    path='issue.md')
            ]
        )

        issues = find_issues_in_commit(self.repo, commit)
        self.assertEqual(len(issues), 1)
        self.assertNotIn('#', issues[0].description)

    def test_two_markdown_issue_cleaned(self):
        commit = self.commit_mock(
            blobs=[
                self.blob_mock(
                    content=
                    b"""
---
@issue 2
@description 
value that has some contents
---
---
@issue 3
@description 
value that has some contents
---
                    """,
                    mime_type='text/plain',
                    path='issue.md')
            ]
        )

        issues = find_issues_in_commit(self.repo, commit)
        self.assertEqual(len(issues), 2)
        self.assertNotIn('#', issues[0].description)

    def test_no_issues_one_changed_supported_file_no_pattern(self):
        commit = self.commit_mock(
            blobs=[
                self.blob_mock(
                    content=b'<!--@issue 3\nvalue that has some contents-->',
                    mime_type='text',
                    path='README.html')
            ]
        )

        issues = find_issues_in_commit(self.repo, commit)
        self.assertEqual(len(issues), 1)

    def test_no_issues_one_changed_unsupported_file_no_pattern(self):
        commit = self.commit_mock(
            blobs=[
                self.blob_mock(
                    content=b'<!--@issue 3\nvalue that has some contents-->',
                    mime_type='text',
                    path='picture.png')
            ]
        )

        issues = find_issues_in_commit(self.repo, commit)
        self.assertFalse(issues)

    def test_no_issues_multiple_changed_files(self):
        commit = self.commit_mock(
            blobs=[
                self.blob_mock(
                    content=''.join(random_40_chars()).encode(),
                    mime_type='text',
                    path='README'+str(i)
                ) for i in range(6)
            ],
            commit_files=['README1', 'README3']
        )

        issues = find_issues_in_commit(self.repo, commit, pattern)
        self.assertFalse(issues)

    def test_no_issues_renamed_file_change(self):
        commit = self.commit_mock(
            blobs=[
                self.blob_mock(
                    content=''.join(random_40_chars()).encode(),
                    mime_type='text',
                    path='README'+str(i)
                ) for i in range(6)
            ],
            commit_files=['docs/this.py', 'README3']
        )

        issues = find_issues_in_commit(self.repo, commit, pattern)
        self.assertFalse(issues)

    def test_no_issues_multiple_changed_files_in_trees(self):

        commit = self.commit_mock(
            trees=[
                self.tree_mock(
                    blobs=[
                        self.blob_mock(
                            content=''.join(random_40_chars()).encode(),
                            mime_type='text',
                            path='docs/file' + str(i) + '.py'
                        ) for i in range(12)
                    ]
                )
            ],
            blobs=[
                self.blob_mock(
                    content=''.join(random_40_chars()).encode(),
                    mime_type='text',
                    path='README'+str(i)
                ) for i in range(6)
            ],
            commit_files=['README1', 'README3', 'docs/file9.py']
        )

        issues = find_issues_in_commit(self.repo, commit, pattern)
        self.assertFalse(issues)

    def test_skips_unicode_error_one_file(self):

        commit = self.commit_mock(
            blobs=[
                self.blob_mock(
                    content='value that has some contents',
                    mime_type='text',
                    path='README')
            ],
            commit_files=['README']
        )

        issues = find_issues_in_commit(self.repo, commit, pattern)
        self.assertFalse(issues)

    def test_contains_issues_multiple_changed_files(self):
        commit = self.commit_mock(
            blobs=[
                self.blob_mock(
                    content=('#@issue ' + str(i)).encode(),
                    mime_type='text',
                    path='README' + str(i)
                ) for i in range(6)
            ],
            commit_files=['README0', 'README1', 'README2']
        )
        issues = find_issues_in_commit(self.repo, commit, pattern)
        self.assertEqual(len(issues), 3)

    def test_contains_issues_multiple_changed_files_multiple_trees(self):
        commit = self.commit_mock(
            trees=[
                self.tree_mock(
                    blobs=[
                        self.blob_mock(
                            content=('#@issue w' + str(i)).encode(),
                            mime_type='text',
                            path='docs/file' + str(i) + '.py'
                        ) for i in range(12)
                    ]
                )
            ],
            blobs=[
                self.blob_mock(
                    content=('#@issue ' + str(i)).encode(),
                    mime_type='text',
                    path='README' + str(i)
                ) for i in range(6)
            ],
            commit_files=['README0', 'README1', 'README2', 'docs/file3.py', 'docs/file7.py']
        )

        commit.tree.blobs[3].contents = b'This one has no issue in it'

        issues = find_issues_in_commit(self.repo, commit, pattern)
        self.assertEqual(len(issues), 5)

    @patch('builtins.open', mock_open(read_data='README*'))
    def test_commit_ignores_certain_files(self):
        commit = self.commit_mock(
            blobs=[
                self.blob_mock(
                    content=('#@issue ' + str(i)).encode(),
                    mime_type='text',
                    path='README' + str(i)
                ) for i in range(6)
            ],
            commit_files=['README0', 'README1', 'README2']
        )

        commit.tree.blobs[3].contents = b'This one has no issue in it'

        ignored_files = get_sciit_ignore(self.repo)
        issues = find_issues_in_commit(self.repo, commit, pattern, ignored_files)
        self.assertEqual(len(issues), 0)

    def test_commit_skip_ignore_file_does_not_exist(self):
        commit = self.commit_mock(
            blobs=[
                self.blob_mock(
                    content=('#@issue ' + str(i)).encode(),
                    mime_type='text',
                    path='README' + str(i)
                ) for i in range(6)
            ],
            commit_files=['README0', 'README1', 'README2']
        )

        with patch('os.path.exists') as p:
            p.return_value = False
            ignored_files = get_sciit_ignore(self.repo)
        issues = find_issues_in_commit(self.repo, commit, pattern, ignored_files)
        self.assertEqual(len(issues), 3)

class TestFindIssueInComment(TestCase):

    def test_no_issue_data_if_id_not_specified(self):
        comment = """
        @description here is a description of the item
        """
        data = find_issue_data_in_comment(comment)
        self.assertEqual(data, {})

    def test_find_id_only(self):
        comment = """
        @issue 2
        """
        data = find_issue_data_in_comment(comment)
        self.assertIn('id', data)
        self.assertEqual(data['id'], '2')

    def test_find_id_and_title(self):
        comment = """
        @issue something-new
        @title this is different
        """
        data = find_issue_data_in_comment(comment)
        self.assertIn('id', data)
        self.assertEqual(data['id'], 'something-new')
        self.assertIn('title', data)
        self.assertEqual(data['title'], 'this is different')

    def test_find_id_and_description_inline(self):
        comment = """
        @issue 2
        @description something will be found
        """
        data = find_issue_data_in_comment(comment)
        self.assertIn('id', data)
        self.assertEqual(data['id'], '2')
        self.assertIn('description', data)
        self.assertIn('something will be found', data['description'])

    def test_find_id_and_description_newline(self):
        comment = """
        @issue 2
        @description 
                something will be found
        """
        data = find_issue_data_in_comment(comment)
        self.assertIn('id', data)
        self.assertEqual(data['id'], '2')
        self.assertIn('description', data)
        self.assertIn('something will be found', data['description'])

    def test_find_id_and_description_between_metadata(self):
        comment = """
        @issue 2
        @description 
            something will be found
        @due_date today
        """
        data = find_issue_data_in_comment(comment)
        self.assertIn('id', data)
        self.assertEqual(data['id'], '2')
        self.assertIn('description', data)
        self.assertIn('something will be found', data['description'])

    def test_find_id_and_assignees(self):
        comment = """
        @issue 2
        @assignees mark, peter, paul
        """
        data = find_issue_data_in_comment(comment)
        self.assertIn('id', data)
        self.assertEqual(data['id'], '2')
        self.assertIn('assignees', data)
        self.assertEqual(data['assignees'], 'mark, peter, paul')

    def test_find_id_and_due_date(self):
        comment = """
        @issue 2
        @due_date 10 dec 2018
        """
        data = find_issue_data_in_comment(comment)
        self.assertIn('id', data)
        self.assertEqual(data['id'], '2')
        self.assertIn('due_date', data)
        self.assertEqual(data['due_date'], '10 dec 2018')

    def test_find_id_and_label(self):
        comment = """
        @issue 2
        @label in-development, main-feature
        """
        data = find_issue_data_in_comment(comment)
        self.assertIn('id', data)
        self.assertEqual(data['id'], '2')
        self.assertIn('label', data)
        self.assertEqual(data['label'], 'in-development, main-feature')

    def test_find_id_and_weight(self):
        comment = """
        @issue 2
        @weight 7
        """
        data = find_issue_data_in_comment(comment)
        self.assertIn('id', data)
        self.assertEqual(data['id'], '2')
        self.assertIn('weight', data)
        self.assertEqual(data['weight'], '7')

    def test_find_id_and_priority(self):
        comment = """
        @issue 2
        @priority mid-high
        """
        data = find_issue_data_in_comment(comment)
        self.assertIn('id', data)
        self.assertEqual(data['id'], '2')
        self.assertIn('priority', data)
        self.assertEqual(data['priority'], 'mid-high')

    def test_find_all_metadata(self):
        comment = """
        @issue the-title-of-your-issue
        @title The Title of Your Issue
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
        self.assertIn('id', data)
        self.assertEqual(data['id'], 'the-title-of-your-issue')
        self.assertIn('title', data)
        self.assertEqual(data['title'], 'The Title of Your Issue')
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

