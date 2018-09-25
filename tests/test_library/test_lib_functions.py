import os
from unittest import TestCase
from unittest.mock import patch, MagicMock

from git import Commit
from git.util import hex_to_bin
from sciit import Issue, IssueCommit, IssueRepo, IssueTree
from sciit.errors import RepoObjectDoesNotExistError, RepoObjectExistsError
from sciit.functions import (deserialize, get_location, get_type_from_sha,
                             object_exists, serialize, cache_history)
from tests.external_resources import safe_create_repo_dir


@patch('sciit.issue.Issue', autospec=True)
class TestGetLocation(TestCase):

    def test_correct_folder_location(self, issue):
        issue.repo.issue_objects_dir = '/here'
        issue.hexsha = 'hexsha'
        folder, filename = get_location(issue)
        self.assertEqual('/here/he', folder)
        self.assertEqual('/here/he/xsha', filename)

    def test_correct_sha_folder_location(self, issue):
        issue.repo.issue_objects_dir = '/here'
        issue.hexsha = 'a7f58a19bff02e266b5b4ac59119b06461f33355'
        folder, filename = get_location(issue)
        self.assertEqual('/here/a7', folder)
        self.assertEqual(
            '/here/a7/f58a19bff02e266b5b4ac59119b06461f33355', filename)


@patch('sciit.functions.get_location', return_value=('here', 'here/a/file'))
class TestObjectExists(TestCase):

    def test_object_does_not_exist(self, get_location):
        self.assertFalse(object_exists(object))

    def test_object_exists(self, get_location):
        safe_create_repo_dir('here')
        os.makedirs('here/a')
        open('here/a/file', 'a').close()
        self.assertTrue(object_exists(object))


class TestSerializeDeserializeObject(TestCase):

    @classmethod
    @patch('sciit.issue.Issue', autospec=True)
    def setUpClass(cls, obj):
        cls.data = {'filepath': 'here', 'contents': {
            'things': 1, 'item': '#Issue for getting it right'}}
        cls.obj = obj
        cls.obj.type = 'sometype'
        cls.obj.repo.issue_objects_dir = 'here'
        cls.obj.data = cls.data.copy()
        cls.obj.size = None

    def setUp(self):
        safe_create_repo_dir('here')

    def test_serialize_object(self):
        self.obj.hexsha = '23asdecs'
        result = serialize(self.obj)
        self.assertTrue(os.path.exists('here/23/asdecs'))
        self.assertTrue(result.size > 0)

    def test_serialize_object_exists(self):
        self.obj.hexsha = '23ssqwasd'
        serialize(self.obj)
        with self.assertRaises(RepoObjectExistsError) as context:
            serialize(self.obj)
        self.assertTrue(
            'The repository object already exists.' in str(context.exception))

    def test_deserialize_object(self):
        self.obj.hexsha = '35aniias1s'
        serialize(self.obj)
        result = deserialize(self.obj)
        self.assertTrue(os.path.exists('here/35/aniias1s'))
        self.assertTrue(result.size > 0)
        self.assertEqual(self.data, result.data)

    def test_deserialize_object_does_not_exists(self):
        with self.assertRaises(RepoObjectDoesNotExistError) as context:
            deserialize(self.obj)
        self.assertTrue(
            'does not exist.' in str(context.exception))


class TestGetTypeFromSha(TestCase):

    @classmethod
    def setUpClass(cls):
        safe_create_repo_dir('here')

        data = {'id': '3', 'title': 'clean up this mess',
                'filepath': 'here'}

        cls.repo = IssueRepo(issue_dir='here')

        cls.issue = Issue.create(cls.repo, data)
        cls.itree = IssueTree.create(cls.repo, [cls.issue, ])
        cls.icommit = IssueCommit.create(
            cls.repo, cls.repo.head.commit, cls.itree)

    def test_object_type_is_issue(self):
        obj_type = get_type_from_sha(self.repo, self.issue.hexsha)
        self.assertTrue(obj_type, 'issue')

    def test_object_type_is_issue_tree(self):
        obj_type = get_type_from_sha(self.repo, self.itree.hexsha)
        self.assertTrue(obj_type, 'issuetree')

    def test_object_type_is_issue_commit(self):
        obj_type = get_type_from_sha(self.repo, self.icommit.hexsha)
        self.assertTrue(obj_type, 'issuecommit')

    def test_object_type_cannot_be_found_in_repo(self):
        with self.assertRaises(RepoObjectDoesNotExistError) as context:
            get_type_from_sha(self.repo, 'self.issue.hexsha')
            self.assertTrue(
                'The repository object does not exist.' in str(context.exception))


class TestCacheIssueHistory(TestCase):

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
                {'id': '6', 'title': 'the contents of the file', 'filepath': 'path',
                 'description': 'here is a nice description'}]

        new_data = [{'id': '1', 'title': 'the contents of the file', 'filepath': 'path'},
                    {'id': '2', 'title': 'the contents of the file', 'filepath': 'path'},
                    {'id': '9', 'title': 'the contents of the file', 'filepath': 'path'},
                    {'id': '6', 'title': 'the contents of the file', 'filepath': 'path',
                     'description': 'description has changed'},
                    {'id': '12', 'title': 'the contents of the file', 'filepath': 'path',
                     'description': 'here is a nice description'}]
        cls.issues = []
        cls.new_issues = []
        for d in data:
            cls.issues.append(Issue.create(cls.repo, d))
        cls.itree = IssueTree.create(cls.repo, cls.issues)

        for d in new_data:
            cls.new_issues.append(Issue.create(cls.repo, d))
        cls.new_itree = IssueTree.create(cls.repo, cls.new_issues)

        cls.head = '622918a4c6539f853320e06804f73d1165df69d0'
        cls.first = '43e8d11ec2cb9802151533ae8d9c5dcc5dec91a4'
        cls.head_commit = Commit(cls.repo, hex_to_bin(cls.head))
        cls.first_commit = Commit(cls.repo, hex_to_bin(cls.first))
        cls.head_icommit = IssueCommit.create(
            cls.repo, cls.head_commit, cls.new_itree)
        IssueCommit.create(cls.repo, cls.first_commit, cls.itree)

    @patch('sciit.repo.IssueRepo.iter_commits')
    @patch('sciit.repo.IssueRepo.heads')
    def test_cache_build_history(self, heads, commits):
        val = [self.head_commit, self.first_commit]
        commits.return_value = val
        head = MagicMock()
        head.commit = self.head_icommit
        head.name = 'master'
        heads.__iter__.return_value = [head]
        history = self.repo.build_history('--all')
        cache_history(self.repo.issue_dir, history)
        stats = os.stat(self.repo.issue_dir + '/HISTORY')
        self.assertTrue(stats.st_size > 1000)
