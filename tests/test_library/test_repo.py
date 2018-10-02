import os
from unittest import TestCase
from unittest.mock import patch, PropertyMock, MagicMock
from git import Commit
from git.util import hex_to_bin
from sciit import IssueRepo, IssueListInCommit, IssueSnapshot
from sciit.functions import write_last_issue_commit_sha, get_last_issue_commit_sha
from sciit.errors import EmptyRepositoryError, NoCommitsError

from tests.external_resources import safe_create_repo_dir, remove_existing_repo


class TestIssueRepoExistingRepository(TestCase):

    def setUp(self):
        safe_create_repo_dir('here')

    def test_issue_repo_is_init(self):
        repo = IssueRepo('here')
        self.assertTrue(repo.is_init())

    def test_reset_init_repo(self):
        repo = IssueRepo('here')
        repo.reset()
        self.assertFalse(os.path.exists('here'))


class TestIssueRepoNoExistingRepository(TestCase):

    def setUp(self):
        remove_existing_repo('here')

    def test_issue_repo_is_not_init(self):
        repo = IssueRepo('here')
        self.assertFalse(repo.is_init())

    def test_issue_repo_setup(self):
        repo = IssueRepo('here')
        repo.git_dir = repo.issue_dir
        repo.setup_file_system_resources()
        self.assertTrue(os.path.exists('here/hooks/post-commit'))
        self.assertTrue(os.path.exists('here/hooks/post-checkout'))
        self.assertTrue(os.path.exists('here/hooks/post-merge'))

    def test_reset_non_init_repo(self):
        repo = IssueRepo('here')
        with self.assertRaises(EmptyRepositoryError) as context:
            repo.reset()
        self.assertTrue(
            'The issue repository is empty.' in str(context.exception))


class TestBuildIssueRepo(TestCase):

    def setUp(self):
        safe_create_repo_dir('here')
        self.repo = IssueRepo('here')

    @patch('sciit.repo.IssueRepo.heads', new_callable=PropertyMock)
    def test_build_from_empty_repo(self, heads):
        heads.return_value = []
        with self.assertRaises(NoCommitsError) as context:
            self.repo.cache_issue_commits_from_all_commits()
        self.assertTrue(
            'The repository has no commits.' in str(context.exception))
        heads.assert_called_once()


class TestBuildIterIssueCommits(TestCase):

    def setUp(self):
        safe_create_repo_dir('here')
        self.repo = IssueRepo('here')

        data = [{'issue_id': '1', 'title': 'the contents of the file', 'filepath': 'path',
                 'description': 'This issue had a description'},
                {'issue_id': '2', 'title': 'the contents of the file', 'filepath': 'path'},
                {'issue_id': '3', 'title': 'the contents of the file', 'filepath': 'path'},
                {'issue_id': '4', 'title': 'the contents of the file', 'filepath': 'path'},
                {'issue_id': '5', 'title': 'the contents of the file', 'filepath': 'path'},
                {'issue_id': '6', 'title': 'the contents of the file', 'filepath': 'path',
                 'description': 'here is a nice description'}]

        new_data = [{'issue_id': '1', 'title': 'the contents of the file', 'filepath': 'path'},
                    {'issue_id': '2', 'title': 'the contents of the file', 'filepath': 'path'},
                    {'issue_id': '9', 'title': 'the contents of the file', 'filepath': 'path'},
                    {'issue_id': '6', 'title': 'the contents of the file', 'filepath': 'path',
                     'description': 'description has changed'},
                    {'issue_id': '12', 'title': 'the contents of the file', 'filepath': 'path',
                     'description': 'here is a nice description'}]

        self.issues = [IssueSnapshot.create_from_data(self.repo, d) for d in data]
        self.new_issues = [IssueSnapshot.create_from_data(self.repo, d) for d in new_data]

        self.head = '622918a4c6539f853320e06804f73d1165df69d0'
        self.first = '43e8d11ec2cb9802151533ae8d9c5dcc5dec91a4'
        self.head_commit = Commit(self.repo, hex_to_bin(self.head))
        self.first_commit = Commit(self.repo, hex_to_bin(self.first))
        self.head_issue_commit = IssueListInCommit.create_from_commit_and_issues(self.repo, self.head_commit, self.new_issues)
        IssueListInCommit.create_from_commit_and_issues(self.repo, self.first_commit, self.issues)

    @patch('sciit.repo.IssueRepo.iter_commits')
    @patch('sciit.repo.IssueRepo.heads')
    def test_get_build_history(self, heads, commits):
        val = [self.head_commit, self.first_commit]
        commits.return_value = val
        head = MagicMock()
        head.commit = self.head_issue_commit
        head.name = 'master'
        heads.__iter__.return_value = [head]
        history = self.repo.build_history('--all')
        self.assertEqual(len(history), 8)
        self.assertEqual(2, len(history['6'].revisions))
        print(history['6'].revisions[0]['changes']['description'])
        self.assertTrue('description has changed' in history['6'].revisions[0]['changes']['description'])
        self.assertTrue('This issue had a description' in history['1'].revisions[0]['changes']['description'])

    @patch('sciit.repo.IssueRepo.heads')
    def test_get_build_history_no_commits(self, heads):
        repo = IssueRepo()
        repo.heads = False
        with self.assertRaises(NoCommitsError) as context:
            repo.build_history('--all')
        self.assertTrue('The repository has no commits.' in str(context.exception))

    @patch('sciit.repo.IssueRepo.iter_commits')
    @patch('sciit.repo.IssueRepo.heads')
    def test_get_open_issues(self, heads, commits):
        val = [self.head_commit, self.first_commit]
        commits.return_value = val
        head = MagicMock()
        head.commit = self.head_issue_commit
        head.name = 'master'
        heads.__iter__.return_value = [head]
        open_issues = self.repo.open_issues
        self.assertEqual(len(open_issues), 5)

    @patch('sciit.repo.IssueRepo.iter_commits')
    @patch('sciit.repo.IssueRepo.heads')
    def test_get_all_issues(self, heads, commits):
        val = [self.head_commit, self.first_commit]
        commits.return_value = val
        head = MagicMock()
        head.commit = self.head_issue_commit
        head.name = 'master'
        heads.__iter__.return_value = [head]
        all_issues = self.repo.all_issues
        self.assertEqual(len(all_issues), 8)

    @patch('sciit.repo.IssueRepo.iter_commits')
    @patch('sciit.repo.IssueRepo.heads')
    def test_get_closed_issues(self, heads, commits):
        val = [self.head_commit, self.first_commit]
        commits.return_value = val
        head = MagicMock()
        head.commit = self.head_issue_commit
        head.name = 'master'
        heads.__iter__.return_value = [head]
        closed_issues = self.repo.closed_issues
        self.assertEqual(len(closed_issues), 3)


class TestIssueStatus(TestCase):

    def setUp(self):
        safe_create_repo_dir('here')
        self.repo = IssueRepo('here')

    @patch('sciit.repo.IssueRepo.iter_commits')
    def test_return_two_known_issue_commits(self, iter_commits):
        # get first two commits of this repo
        first = '43e8d11ec2cb9802151533ae8d9c5dcc5dec91a4'
        second = '622918a4c6539f853320e06804f73d1165df69d0'
        val = [Commit(self.repo, hex_to_bin(second)), Commit(self.repo, hex_to_bin(first))]
        iter_commits.return_value = val

        data = {'issue_id': '1', 'title': 'hello world', 'filepath': 'README.md'}
        issue = IssueSnapshot.create_from_data(self.repo, data)
        IssueListInCommit.create_from_commit_and_issues(self.repo, val[1], [issue])
        IssueListInCommit.create_from_commit_and_issues(self.repo, val[0], [issue])

        issue_commits = list(self.repo.iter_issue_commits('--all'))

        self.assertEqual(issue_commits[1].hexsha, val[1].hexsha)
        self.assertEqual(issue_commits[0].hexsha, val[0].hexsha)


class TestRepoSync(TestCase):

    @classmethod
    def setUpClass(cls):
        safe_create_repo_dir('here')
        cls.repo = IssueRepo('here')
        cls.head = '622918a4c6539f853320e06804f73d1165df69d0'
        cls.first = '43e8d11ec2cb9802151533ae8d9c5dcc5dec91a4'
        cls.head_commit = Commit(cls.repo, hex_to_bin(cls.head))
        cls.first_commit = Commit(cls.repo, hex_to_bin(cls.first))

    @patch('sciit.repo.IssueRepo.iter_commits')
    @patch('sciit.repo.IssueRepo.heads')
    def test_sync_repository(self, heads, commits):
        val = [self.head_commit, self.first_commit]
        write_last_issue_commit_sha(self.repo.issue_dir, self.first)
        commits.return_value = val
        head = MagicMock()
        head.commit = self.head_commit
        head.name = 'master'
        heads.__iter__.return_value = [head]
        self.repo.sync()
        last = get_last_issue_commit_sha(self.repo.issue_dir)
        self.assertEqual(last, self.head)
