import os
from unittest import TestCase
from unittest.mock import patch, MagicMock

from git import Commit
from git.util import hex_to_bin
from sciit import Issue, IssueCommit, IssueRepo, IssueTree
from sciit.errors import RepoObjectDoesNotExistError, RepoObjectExistsError
from sciit.functions import deserialize_repository_object_from_json, get_repository_object_path, \
    get_repository_object_type_from_sha, get_repository_object_size, repository_object_exists,\
    serialize_repository_object_as_json, cache_history
from tests.external_resources import safe_create_repo_dir, remove_existing_repo


@patch('sciit.issue.Issue', autospec=True)
class TestGetLocation(TestCase):

    def test_correct_folder_location(self, issue):
        issue.repo.issue_objects_dir = '/here'
        issue.hexsha = 'hexsha'
        path = get_repository_object_path(issue.repo, issue.hexsha)
        self.assertEqual('/here/he/xsha', path)

    def test_correct_sha_folder_location(self, issue):
        issue.repo.issue_objects_dir = '/here'
        issue.hexsha = 'a7f58a19bff02e266b5b4ac59119b06461f33355'
        path = get_repository_object_path(issue.repo, issue.hexsha)
        self.assertEqual('/here/a7/f58a19bff02e266b5b4ac59119b06461f33355', path)


@patch('sciit.functions.get_repository_object_path', return_value='here/a/file')
class TestObjectExists(TestCase):

    def test_object_does_not_exist(self, get_repository_object_path):
        mock_repository = MagicMock()
        mock_sha = 'abc'
        self.assertFalse(repository_object_exists(mock_repository, mock_sha))

    def test_object_exists(self, get_repository_object_path):
        safe_create_repo_dir('here')
        os.makedirs('here/a')
        open('here/a/file', 'a').close()

        mock_repository = MagicMock()
        mock_sha = 'abc'

        self.assertTrue(repository_object_exists(mock_repository, mock_sha))

    def tearDown(self):
        remove_existing_repo('here')


class TestSerializeDeserializeObject(TestCase):

    def setUp(self):

        safe_create_repo_dir('here')
        self.repo = MagicMock()
        self.repo.issue_objects_dir = 'here'

        self.data = {'filepath': 'here', 'contents': {'things': 1, 'item': '#Issue for getting it right'}}
        self.hexsha = '1234'

    def test_serialize_object(self):
        self.hexsha = '23asdecs'
        serialize_repository_object_as_json(self.repo, self.hexsha, Issue, self.data)
        self.assertTrue(os.path.exists('here/23/asdecs'))
        self.assertTrue(get_repository_object_size(self.repo, self.hexsha) > 0)

    def test_serialize_object_exists(self):
        self.hexsha = '23ssqwasd'
        serialize_repository_object_as_json(self.repo, self.hexsha, Issue, self.data)
        with self.assertRaises(RepoObjectExistsError) as context:
            serialize_repository_object_as_json(self.repo, self.hexsha, Issue, self.data)
        self.assertTrue(
            'The repository object already exists.' in str(context.exception))

    def test_deserialize_object(self):
        self.hexsha = '35aniias1s'
        serialize_repository_object_as_json(self.repo, self.hexsha, Issue, self.data)
        self.data, self.size = deserialize_repository_object_from_json(self.repo, self.hexsha)
        self.assertTrue(os.path.exists('here/35/aniias1s'))
        self.assertTrue(self.size > 0)
        self.assertEqual(self.data, self.data)

    def test_deserialize_object_does_not_exists(self):
        with self.assertRaises(RepoObjectDoesNotExistError) as context:
            deserialize_repository_object_from_json(self.repo, self.hexsha)
        self.assertTrue('does not exist.' in str(context.exception))


class TestGetTypeFromSha(TestCase):

    @classmethod
    def setUpClass(self):
        safe_create_repo_dir('here')

        data = {'id': '3', 'title': 'clean up this mess',
                'filepath': 'here'}

        self.repo = IssueRepo(issue_dir='here')

        self.issue = Issue.create_from_data(self.repo, data)
        self.itree = IssueTree.create(self.repo, [self.issue, ])
        self.icommit = IssueCommit.create(
            self.repo, self.repo.head.commit, self.itree)

    def test_object_type_is_issue(self):
        obj_type = get_repository_object_type_from_sha(self.repo, self.issue.hexsha)
        self.assertTrue(obj_type, 'issue')

    def test_object_type_is_issue_tree(self):
        obj_type = get_repository_object_type_from_sha(self.repo, self.itree.hexsha)
        self.assertTrue(obj_type, 'issuetree')

    def test_object_type_is_issue_commit(self):
        obj_type = get_repository_object_type_from_sha(self.repo, self.icommit.hexsha)
        self.assertTrue(obj_type, 'issuecommit')

    def test_object_type_cannot_be_found_in_repo(self):
        with self.assertRaises(RepoObjectDoesNotExistError) as context:
            get_repository_object_type_from_sha(self.repo, 'self.issue.hexsha')
            self.assertTrue(
                'The repository object does not exist.' in str(context.exception))


class TestCacheIssueHistory(TestCase):

    @classmethod
    def setUpClass(self):
        safe_create_repo_dir('here')
        self.repo = IssueRepo('here')

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
        self.issues = []
        self.new_issues = []
        for d in data:
            self.issues.append(Issue.create_from_data(self.repo, d))
        self.itree = IssueTree.create(self.repo, self.issues)

        for d in new_data:
            self.new_issues.append(Issue.create_from_data(self.repo, d))
        self.new_itree = IssueTree.create(self.repo, self.new_issues)

        self.head = '622918a4c6539f853320e06804f73d1165df69d0'
        self.first = '43e8d11ec2cb9802151533ae8d9c5dcc5dec91a4'
        self.head_commit = Commit(self.repo, hex_to_bin(self.head))
        self.first_commit = Commit(self.repo, hex_to_bin(self.first))
        self.head_icommit = IssueCommit.create(
            self.repo, self.head_commit, self.new_itree)
        IssueCommit.create(self.repo, self.first_commit, self.itree)

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
