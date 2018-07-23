"""
This module tests the functionality of the functions module.
"""
import os
from unittest import TestCase
from unittest.mock import patch

from sciit import Issue, IssueCommit, IssueRepo, IssueTree
from sciit.errors import RepoObjectDoesNotExistError, RepoObjectExistsError
from sciit.functions import (deserialize, get_location, get_type_from_sha,
                             object_exists, serialize)
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
            'The repository object does not exist.' in str(context.exception))


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
