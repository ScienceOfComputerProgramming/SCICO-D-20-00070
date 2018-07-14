"""
This module tests the functionality of the functions module.
"""
import sys
import os
import shutil
from unittest import TestCase
from unittest.mock import patch
from gitissue import IssueRepo, Issue, IssueTree, IssueCommit
from gitissue.functions import get_location, object_exists, \
    get_type_from_sha, save_issue_history, get_issue_history
from gitissue.functions import serialize, deserialize
from gitissue.errors import RepoObjectExistsError, \
    RepoObjectDoesNotExistError, NoIssueHistoryError


class TestObject():
    __slots__ = ('data', 'size', 'type')

    def __init__(self):
        super(TestObject, self).__init__()


@patch('gitissue.issue.Object', autospec=True)
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


@patch('gitissue.functions.get_location', return_value=('here', 'here/a/file'))
class TestObjectExists(TestCase):

    def test_object_does_not_exist(self, get_location):
        self.assertFalse(object_exists(object))

    def test_object_exists(self, get_location):
        os.makedirs('here')
        os.makedirs('here/a')
        open('here/a/file', 'a').close()
        self.assertTrue(object_exists(object))
        shutil.rmtree('here')


@patch('gitissue.functions.get_location', return_value=('here/a', 'here/a/file'))
class TestSerializeDeserializeObject(TestCase):

    data = {'filepath': 'here', 'contents': {
            'things': 1, 'item': '#Issue for getting it right'}}

    @classmethod
    def setUpClass(cls):
        os.makedirs('here')
        os.makedirs('here/a')

    def setUp(self):
        self.obj = TestObject()
        self.obj.type = 'sometype'

    def test1_serialize_object(self, get_location):
        self.obj.data = TestSerializeDeserializeObject.data.copy()
        self.obj.size = None

        result = serialize(self.obj)
        self.assertTrue(os.path.exists('here/a/file'))
        self.assertTrue(result.size > 0)

    def test2_serialize_object_new_folder(self, get_location):
        get_location.return_value = ('here/b', 'here/b/file')
        self.obj.data = TestSerializeDeserializeObject.data.copy()
        self.obj.size = None

        result = serialize(self.obj)
        self.assertTrue(os.path.exists('here/a/file'))
        self.assertTrue(result.size > 0)

    def test3_serialize_object_exists(self, get_location):
        get_location.return_value = ('here/b', 'here/b/file')
        self.obj.data = TestSerializeDeserializeObject.data.copy()
        self.obj.size = None

        with self.assertRaises(RepoObjectExistsError) as context:
            serialize(self.obj)
        self.assertTrue(
            'The repository object already exists.' in str(context.exception))

    def test4_deserialize_object(self, get_location):
        result = deserialize(self.obj)
        self.assertTrue(os.path.exists('here/a/file'))
        self.assertTrue(result.size > 0)
        self.assertEqual(TestSerializeDeserializeObject.data, result.data)

    def test5_deserialize_object_does_not_exists(self, get_location):
        get_location.return_value = ('here/c', 'here/c/file')
        with self.assertRaises(RepoObjectDoesNotExistError) as context:
            deserialize(self.obj)
        self.assertTrue(
            'The repository object does not exist.' in str(context.exception))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree('here')


class TestGetTypeFromSha(TestCase):

    @classmethod
    def setUpClass(cls):
        os.makedirs('here')
        os.makedirs('here/a')

        data = {'id': '3', 'title': 'clean up this mess',
                'filepath': 'here'}

        cls.repo = IssueRepo()
        cls.repo.issue_dir = 'here'
        cls.repo.issue_objects_dir = 'here/a'

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

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree('here')


class TestIssueHistory(TestCase):

    @classmethod
    def setUpClass(cls):
        os.makedirs('here')
        os.makedirs('here/a')

        cls.repo = IssueRepo()
        cls.repo.issue_dir = 'here'
        cls.repo.issue_objects_dir = 'here/a'

        cls.issues = []
        for i in range(6):
            d = {'id': str(i), 'title': 'clean up this mess',
                 'filepath': 'here'}
            cls.issues.append(Issue.create(cls.repo, d))

    @patch('gitissue.IssueTree', autospec=True)
    def test1_does_not_create_new_history(self, itree):
        itree.repo = self.repo
        itree.issues = []
        save_issue_history(itree)
        self.assertFalse(os.path.exists(self.repo.issue_dir + '/HISTORY'))

    @patch('gitissue.IssueTree', autospec=True)
    def test2_no_history_error(self, itree):
        with self.assertRaises(NoIssueHistoryError) as context:
            get_issue_history(self.repo)
        self.assertTrue(
            'The repository does not contain any issues.' in str(context.exception))

    @patch('gitissue.IssueTree', autospec=True)
    def test3_creates_new_history(self, itree):
        itree.repo = self.repo
        itree.issues = self.issues
        save_issue_history(itree)
        self.assertTrue(os.path.exists(self.repo.issue_dir + '/HISTORY'))

    @patch('gitissue.IssueTree', autospec=True)
    def test4_gets_history(self, itree):
        contents = get_issue_history(self.repo)
        self.assertEqual(len(contents), 6)
        os.remove(self.repo.issue_dir + '/HISTORY')

    @patch('gitissue.IssueTree', autospec=True)
    def test5_creates_new_duplicate_history(self, itree):
        itree.repo = self.repo
        itree.issues = self.issues
        save_issue_history(itree)
        self.assertTrue(os.path.exists(self.repo.issue_dir + '/HISTORY'))
        contents = get_issue_history(self.repo)
        save_issue_history(itree)
        self.assertTrue(os.path.exists(self.repo.issue_dir + '/HISTORY'))
        contents2 = get_issue_history(self.repo)
        self.assertEqual(contents, contents2)

    @patch('gitissue.IssueTree', autospec=True)
    def test6_adds_to_new_history(self, itree):
        itree.repo = self.repo
        itree.issues = self.issues
        save_issue_history(itree)
        self.assertTrue(os.path.exists(self.repo.issue_dir + '/HISTORY'))
        contents = get_issue_history(self.repo)

        new_data = {'id': '17', 'title': 'newfile', 'filepath': '.gitignore'}
        new_issue = Issue.create(self.repo, new_data)
        itree.issues.append(new_issue)
        save_issue_history(itree)
        self.assertTrue(os.path.exists(self.repo.issue_dir + '/HISTORY'))
        contents2 = get_issue_history(self.repo)

        self.assertNotEqual(contents, contents2)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree('here')
