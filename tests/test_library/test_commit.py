import random
import string
from unittest import TestCase
from unittest.mock import Mock

from pathspec import PathSpec

from sciit.commit import find_issue_snapshots_in_commit_paths_that_changed, find_issue_in_comment

pattern = r'((?:#.*(?:\n\s*#)*.*)|(?:#.*)|(?:#.*$))'


def random_40_chars():
    return [random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(40)]


class TestFindIssuesInCommit(TestCase):

    @staticmethod
    def create_tree_mock(trees=list(), blobs=list()):
        tree = Mock()
        tree.trees = trees
        tree.blobs = blobs
        return tree

    @staticmethod
    def create_commit_mock(trees=list(), blobs=list(), commit_files=None):
        commit = Mock()
        commit.tree = TestFindIssuesInCommit.create_tree_mock(trees, blobs)
        if not commit_files:
            commit_files = [blob.path for blob in commit.tree.blobs]
        commit.stats.files.keys.return_value = commit_files
        commit.parents = list()
        commit.repo.git.execute=Mock(return_value="master")
        return commit

    @staticmethod
    def create_blob_mock(content=None, mime_type=None, path=None):
        blob = Mock()
        blob.path = path
        blob.type = 'blob'
        blob.mime_type = mime_type
        blob.data_stream = Mock()
        blob.data_stream.read = Mock(return_value=content)
        return blob

    def test_no_issues_one_changed_file(self):
        commit = self.create_commit_mock(
            blobs=[
                self.create_blob_mock(
                    content=b'value that has some contents',
                    mime_type='text',
                    path='README')
            ])

        issue_snapshots, _, _ = find_issue_snapshots_in_commit_paths_that_changed(commit, pattern)
        self.assertFalse(issue_snapshots)

    def test_one_cstyle_issue_cleaned(self):
        commit = self.create_commit_mock(
            blobs=[
                self.create_blob_mock(
                    content=b"""
/*@issue 2
 *@description
 * value that has some contents
 */
                    """,
                    mime_type='text/x-java',
                    path='hello.java')
            ]
        )

        issue_snapshots, _, _ = find_issue_snapshots_in_commit_paths_that_changed(commit)
        self.assertEqual(1, len(issue_snapshots))
        self.assertNotIn('*', issue_snapshots[0].description)

    def test_one_python_issue_cleaned(self):
        commit = self.create_commit_mock(
            blobs=[
                self.create_blob_mock(
                    content=b'''
                    """
                    @issue 2
                    @description
                     value that has some contents
                    """
                    ''',
                    mime_type='text/x-python',
                    path='hello.py')
            ]
        )

        issue_snapshots, _, _ = find_issue_snapshots_in_commit_paths_that_changed(commit)
        self.assertEqual(len(issue_snapshots), 1)
        self.assertNotIn('*', issue_snapshots[0].description)

    def test_one_hashstyle_issue_cleaned(self):

        commit = self.create_commit_mock(
            blobs=[
                self.create_blob_mock(
                    content=b"""
#***
# @issue 2
# @description
#  value that has some contents
#***"""
                    ,
                    mime_type='text/plain',
                    path='hello')
            ]
        )

        issue_snapshots, _, _ = find_issue_snapshots_in_commit_paths_that_changed(commit)
        self.assertEqual(1, len(issue_snapshots))
        self.assertNotIn('#', issue_snapshots[0].description)

    def test_one_markdown_issue_cleaned(self):
        commit = self.create_commit_mock(
            blobs=[
                self.create_blob_mock(
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

        issue_snapshots, _, _ = find_issue_snapshots_in_commit_paths_that_changed(commit)
        self.assertEqual(len(issue_snapshots), 1)
        self.assertNotIn('#', issue_snapshots[0].description)

    def test_two_markdown_issue_cleaned(self):
        commit = self.create_commit_mock(
            blobs=[
                self.create_blob_mock(
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

        issue_snapshots, _, _ = find_issue_snapshots_in_commit_paths_that_changed(commit)
        self.assertEqual(len(issue_snapshots), 2)
        self.assertNotIn('#', issue_snapshots[0].description)

    def test_no_issues_one_changed_supported_file_no_pattern(self):
        commit = self.create_commit_mock(
            blobs=[
                self.create_blob_mock(
                    content=b"""
<!--
@issue 3
value that has some contents
-->
""",
                    mime_type='text',
                    path='README.html')
            ]
        )

        issue_snapshots, _, _ = find_issue_snapshots_in_commit_paths_that_changed(commit)
        self.assertEqual(len(issue_snapshots), 1)

    def test_no_issues_one_changed_unsupported_file_no_pattern(self):
        commit = self.create_commit_mock(
            blobs=[
                self.create_blob_mock(
                    content=b"""
<!--
@issue 3
value that has some contents
-->
                    """,
                    mime_type='text',
                    path='picture.png')
            ]
        )

        issue_snapshots, _, _ = find_issue_snapshots_in_commit_paths_that_changed(commit)
        self.assertFalse(issue_snapshots)

    def test_no_issues_multiple_changed_files(self):
        commit = self.create_commit_mock(
            blobs=[
                self.create_blob_mock(
                    content=''.join(random_40_chars()).encode(),
                    mime_type='text',
                    path='README'+str(i)
                ) for i in range(6)
            ],
            commit_files=['README1', 'README3']
        )

        issue_snapshots, _, _ = find_issue_snapshots_in_commit_paths_that_changed(commit, pattern)
        self.assertFalse(issue_snapshots)

    def test_no_issues_renamed_file_change(self):
        commit = self.create_commit_mock(
            blobs=[
                self.create_blob_mock(
                    content=''.join(random_40_chars()).encode(),
                    mime_type='text',
                    path='README'+str(i)
                ) for i in range(6)
            ],
            commit_files=['docs/this.py', 'README3']
        )

        issue_snapshots, _, _ = find_issue_snapshots_in_commit_paths_that_changed(commit, pattern)
        self.assertFalse(issue_snapshots)

    def test_no_issues_multiple_changed_files_in_trees(self):

        commit = self.create_commit_mock(
            trees=[
                self.create_tree_mock(
                    blobs=[
                        self.create_blob_mock(
                            content=''.join(random_40_chars()).encode(),
                            mime_type='text',
                            path='docs/file' + str(i) + '.py'
                        ) for i in range(12)
                    ]
                )
            ],
            blobs=[
                self.create_blob_mock(
                    content=''.join(random_40_chars()).encode(),
                    mime_type='text',
                    path='README'+str(i)
                ) for i in range(6)
            ],
            commit_files=['README1', 'README3', 'docs/file9.py']
        )

        issue_snapshots, _, _ = find_issue_snapshots_in_commit_paths_that_changed(commit, pattern)
        self.assertFalse(issue_snapshots)

    def test_skips_unicode_error_one_file(self):

        commit = self.create_commit_mock(
            blobs=[
                self.create_blob_mock(
                    content='value that has some contents',
                    mime_type='text',
                    path='README')
            ],
            commit_files=['README']
        )

        issue_snapshots, _, _ = find_issue_snapshots_in_commit_paths_that_changed(commit, pattern)
        self.assertFalse(issue_snapshots)

    def test_contains_issues_multiple_changed_files(self):
        commit = self.create_commit_mock(
            blobs=[
                self.create_blob_mock(
                    content=('#@issue ' + str(i)).encode(),
                    mime_type='text',
                    path='README' + str(i)
                ) for i in range(6)
            ],
            commit_files=['README0', 'README1', 'README2']
        )

        commit.tree.blobs[3].contents = b'This one has no issue in it'

        issue_snapshots, _, _ = find_issue_snapshots_in_commit_paths_that_changed(commit, pattern)
        self.assertEqual(len(issue_snapshots), 3)

    def test_contains_issues_multiple_changed_files_multiple_trees(self):
        commit = self.create_commit_mock(
            trees=[
                self.create_tree_mock(
                    blobs=[
                        self.create_blob_mock(
                            content=('#@issue w' + str(i)).encode(),
                            mime_type='text',
                            path='docs/file' + str(i) + '.py'
                        ) for i in range(12)
                    ]
                )
            ],
            blobs=[
                self.create_blob_mock(
                    content=('#@issue ' + str(i)).encode(),
                    mime_type='text',
                    path='README' + str(i)
                ) for i in range(6)
            ],
            commit_files=['README0', 'README1', 'README2', 'docs/file3.py', 'docs/file7.py']
        )

        commit.tree.blobs[3].contents = b'This one has no issue in it'

        issue_snapshots, _, _ = find_issue_snapshots_in_commit_paths_that_changed(commit, pattern)
        self.assertEqual(len(issue_snapshots), 5)

    def test_commit_ignores_certain_files(self):
        commit = self.create_commit_mock(
            blobs=[
                self.create_blob_mock(
                    content=('#@issue ' + str(i)).encode(),
                    mime_type='text',
                    path='README' + str(i)
                ) for i in range(6)
            ],
            commit_files=['README0', 'README1', 'README2']
        )

        commit.tree.blobs[3].contents = b'This one has no issue in it'

        ignored_files = PathSpec.from_lines('gitignore', ['README*'])
        issue_snapshots, _, _ = find_issue_snapshots_in_commit_paths_that_changed(commit, pattern, ignored_files)
        self.assertEqual(len(issue_snapshots), 0)

    def test_commit_skip_ignore_file_does_not_exist(self):
        commit = self.create_commit_mock(
            blobs=[
                self.create_blob_mock(
                    content=('#@issue ' + str(i)).encode(),
                    mime_type='text',
                    path='README' + str(i)
                ) for i in range(6)
            ],
            commit_files=['README0', 'README1', 'README2']
        )

        issue_snapshots, _, _ = find_issue_snapshots_in_commit_paths_that_changed(commit, pattern, None)
        self.assertEqual(3, len(issue_snapshots))


class TestFindIssueInComment(TestCase):

    def test_no_issue_data_if_id_not_specified(self):
        comment = """
        @description here is a description of the item
        """
        data = find_issue_in_comment(comment)
        self.assertEqual(data, {})

    def test_find_id_only(self):
        comment = """
        @issue 2
        """
        data = find_issue_in_comment(comment)
        self.assertIn('issue_id', data)
        self.assertEqual(data['issue_id'], '2')

    def test_find_id_and_title(self):
        comment = """
        @issue something-new
        @title this is different
        """
        data = find_issue_in_comment(comment)
        self.assertIn('issue_id', data)
        self.assertEqual(data['issue_id'], 'something-new')
        self.assertIn('title', data)
        self.assertEqual(data['title'], 'this is different')

    def test_find_id_and_description_inline(self):
        comment = """
        @issue 2
        @description something will be found
        """
        data = find_issue_in_comment(comment)
        self.assertIn('issue_id', data)
        self.assertEqual(data['issue_id'], '2')
        self.assertIn('description', data)
        self.assertIn('something will be found', data['description'])

    def test_find_id_and_description_newline(self):
        comment = """
        @issue 2
        @description 
                something will be found
        """
        data = find_issue_in_comment(comment)
        self.assertIn('issue_id', data)
        self.assertEqual(data['issue_id'], '2')
        self.assertIn('description', data)
        self.assertIn('something will be found', data['description'])

    def test_find_id_and_description_between_metadata(self):
        comment = """
        @issue 2
        @description 
            something will be found
        @due_date today
        """
        data = find_issue_in_comment(comment)
        self.assertIn('issue_id', data)
        self.assertEqual(data['issue_id'], '2')
        self.assertIn('description', data)
        self.assertIn('something will be found', data['description'])

    def test_find_id_and_assignees(self):
        comment = """
        @issue 2
        @assignees mark, peter, paul
        """
        data = find_issue_in_comment(comment)
        self.assertIn('issue_id', data)
        self.assertEqual(data['issue_id'], '2')
        self.assertIn('assignees', data)
        self.assertEqual(data['assignees'], 'mark, peter, paul')

    def test_find_id_and_due_date(self):
        comment = """
        @issue 2
        @due_date 10 dec 2018
        """
        data = find_issue_in_comment(comment)
        self.assertIn('issue_id', data)
        self.assertEqual(data['issue_id'], '2')
        self.assertIn('due_date', data)
        self.assertEqual(data['due_date'], '10 dec 2018')

    def test_find_id_and_label(self):
        comment = """
        @issue 2
        @label in-development, main-feature
        """
        data = find_issue_in_comment(comment)
        self.assertIn('issue_id', data)
        self.assertEqual(data['issue_id'], '2')
        self.assertIn('label', data)
        self.assertEqual(data['label'], 'in-development, main-feature')

    def test_find_id_and_weight(self):
        comment = """
        @issue 2
        @weight 7
        """
        data = find_issue_in_comment(comment)
        self.assertIn('issue_id', data)
        self.assertEqual(data['issue_id'], '2')
        self.assertIn('weight', data)
        self.assertEqual(data['weight'], '7')

    def test_find_id_and_priority(self):
        comment = """
        @issue 2
        @priority mid-high
        """
        data = find_issue_in_comment(comment)
        self.assertIn('issue_id', data)
        self.assertEqual(data['issue_id'], '2')
        self.assertIn('priority', data)
        self.assertEqual(data['priority'], 'mid-high')

    def test_find_all_metadata(self):
        comment = """
        @issue the-title-of-your-issue
        @title The Title of Your IssueSnapshot
        @description:
            A description of you issue as you
            want it to be ``markdown`` supported
        @assignees nystrome, kevin, daniels
        @due date 12 oct 2018
        @label in-development
        @weight 4
        @priority high
        """
        data = find_issue_in_comment(comment)
        self.assertIn('issue_id', data)
        self.assertEqual(data['issue_id'], 'the-title-of-your-issue')
        self.assertIn('title', data)
        self.assertEqual(data['title'], 'The Title of Your IssueSnapshot')
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

