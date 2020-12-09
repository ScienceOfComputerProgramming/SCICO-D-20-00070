import datetime
import os
from unittest import TestCase
from unittest.mock import patch, MagicMock
from sciit import IssueRepo
from sciit.functions import get_last_issue_commit_sha
from sciit.errors import EmptyRepositoryError, NoCommitsError

from tests.external_resources import create_mock_git_repository, remove_existing_repo, create_mock_commit, \
    create_mock_commit_with_issue_snapshots, create_mock_parents


class TestIssueRepoExistingRepository(TestCase):

    def setUp(self):
        self.mock_git_repository = create_mock_git_repository('working_dir', list(), list())

    def test_issue_repo_is_init(self):
        repo = IssueRepo(self.mock_git_repository)
        repo.setup_file_system_resources()
        self.assertTrue(repo.is_init())

    def test_reset_init_repo(self):
        repo = IssueRepo(self.mock_git_repository)
        repo.setup_file_system_resources()
        repo.reset()
        self.assertFalse(os.path.exists('working_dir/.git/issues'))

    def tearDown(self):
        remove_existing_repo('working_dir')


class TestIssueRepoNoExistingRepository(TestCase):

    def setUp(self):
        remove_existing_repo('working_dir')
        self.mock_git_repository = create_mock_git_repository('working_dir', list(), list())

    def test_issue_repo_is_not_init(self):
        repo = IssueRepo(self.mock_git_repository)
        self.assertFalse(repo.is_init())

    def test_issue_repo_setup(self):
        repo = IssueRepo(self.mock_git_repository)
        repo.setup_file_system_resources()
        self.assertTrue(os.path.exists('working_dir/.git/hooks/post-commit'))
        self.assertTrue(os.path.exists('working_dir/.git/hooks/post-merge'))

    def test_reset_non_init_repo(self):
        repo = IssueRepo(self.mock_git_repository)
        with self.assertRaises(EmptyRepositoryError) as context:
            repo.reset()
        self.assertTrue('The issue repository is empty.' in str(context.exception))

    def tearDown(self):
        remove_existing_repo('working_dir')


class TestBuildIssueRepo(TestCase):

    def setUp(self):

        first_data = [
            {'issue_id': '1', 'title': 'the contents of the file', 'file_path': 'path',
             'description': 'This issue had a description'},
            {'issue_id': '2', 'title': 'the contents of the file', 'file_path': 'another/path'},
            {'issue_id': '3', 'title': 'the contents of the file', 'file_path': 'path'},
            {'issue_id': '4', 'title': 'the contents of the file', 'file_path': 'path'},
            {'issue_id': '5', 'title': 'the contents of the file', 'file_path': 'path'},
            {'issue_id': '6', 'title': 'the contents of the file', 'file_path': 'path',
             'description': 'here is a nice description'}
        ]

        self.first_commit, self.first_issue_snapshots =\
            create_mock_commit_with_issue_snapshots(
                '43e8d11ec2cb9802151533ae8d9c5dcc5dec91a4',
                'Nystrome',
                datetime.datetime(2018, 1, 1),
                first_data)

        head_data = [
            {'issue_id': '1', 'title': 'the contents of the file', 'file_path': 'path'},
            {'issue_id': '9', 'title': 'the contents of the file', 'file_path': 'path'},
            {'issue_id': '6', 'title': 'the contents of the file', 'file_path': 'path',
             'description': 'description has changed'},
            {'issue_id': '12', 'title': 'the contents of the file', 'file_path': 'path',
             'description': 'here is a nice description'}
        ]

        self.head_commit, self.head_issue_snapshots =\
            create_mock_commit_with_issue_snapshots(
                '622918a4c6539f853320e06804f73d1165df69d0',
                'Nystrome',
                datetime.datetime(2018, 1, 1),
                head_data,
                create_mock_parents(self.first_commit))

        self.mock_git_repository = create_mock_git_repository(
            'working_dir', [('master', self.head_commit.hexsha)], [self.first_commit, self.head_commit])

        self.issue_repository = IssueRepo(self.mock_git_repository)
        self.issue_repository.setup_file_system_resources()

    def test_build_from_empty_repo(self):
        self.mock_git_repository.heads = list()

        with self.assertRaises(NoCommitsError) as context:
            self.issue_repository.cache_issue_snapshots_from_all_commits()
        self.assertTrue('The repository has no commits.' in str(context.exception))

    @patch('sciit.repo.Commit', new_callable=MagicMock)
    @patch('sciit.repo.find_issue_snapshots_in_commit_paths_that_changed', new_callable=MagicMock)
    def test_build_issue_cache_from_mocked_git_repo(
            self, find_issues_in_commit_paths_that_changed,
            commit_constructor):

        find_issues_in_commit_paths_that_changed.side_effect = [
            [self.first_issue_snapshots, ['path', 'another/path'], ['master']],
            [self.head_issue_snapshots, ['another/path'], ['master']]
        ]
        commit_constructor.side_effect = [self.first_commit] * 6 + [self.head_commit] * 5

        self.issue_repository.cache_issue_snapshots_from_all_commits()
        history = self.issue_repository.get_all_issues()
        self.assertEqual(8, len(history))
        self.assertEqual(2, len(history['1'].revisions))

    def tearDown(self):
        remove_existing_repo('working_dir')


class TestRepoSync(TestCase):

    def setUp(self):

        self.first_commit = create_mock_commit(
            '43e8d11ec2cb9802151533ae8d9c5dcc5dec91a4',
            datetime.datetime(2018, 1, 1),
            list(),
        )

        self.head_commit = create_mock_commit(
            '622918a4c6539f853320e06804f73d1165df69d0',
            datetime.datetime(2018, 1, 1),
            [self.first_commit],
        )

        if not os.path.exists('working_dir'):
            os.mkdir('working_dir')
        os.chdir('working_dir')

        self.mock_git_repository = create_mock_git_repository(
            '.',
            [('master', self.head_commit.hexsha)],
            [self.head_commit, self.first_commit])

        self.repo = IssueRepo(self.mock_git_repository)
        self.repo.setup_file_system_resources()

    @patch('sciit.read_commit._find_branches_for_commit', new_callable=MagicMock())
    def test_sync_repository(self, find_branches_mock):

        find_branches_mock.return_value=['master']

        # write_last_issue_commit_sha(self.repo.issue_dir, self.first)

        self.repo.cache_issue_snapshots_from_unprocessed_commits()
        last = get_last_issue_commit_sha(self.repo.issue_dir)

        self.assertEqual(self.mock_git_repository.head.commit.hexsha, last)

    def tearDown(self):
        os.chdir('../')
        remove_existing_repo('working_dir')

