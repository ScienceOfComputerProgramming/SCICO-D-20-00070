"""
This module tests the functionality of the git.helper module.
"""
from unittest import TestCase
from unittest.mock import patch
from gitissue.tools import repo
from tests import mocks


class TestGetDirectory(TestCase):

    @patch('gitissue.tools.repo.get_src_directory', return_value="/code/repository/")
    def test_valid_git_directory(self, mock):
        self.assertTrue('.git' in repo.get_git_directory())

    @patch('gitissue.tools.repo.get_src_directory', return_value=False)
    def test_false_git_directory(self, mock):
        self.assertFalse(repo.get_git_directory())

    @patch('gitissue.tools.repo.run_command', return_value="/code/repository")
    def test_valid_src_directory(self, mock):
        self.assertTrue('code' in repo.get_src_directory())

    @patch('gitissue.tools.repo.run_command', return_value="")
    def test_false_src_directory(self, mock):
        self.assertFalse(repo.get_src_directory())


class TestGetRemoteType(TestCase):

    @patch('gitissue.tools.repo.run_command', return_value='github.com')
    def test_found_one_supported_remote_type(self, mock):
        types = repo.get_git_remote_type()
        self.assertIn('github', types)

    @patch('gitissue.tools.repo.run_command', return_value='github.com\ngitlab.com')
    def test_found_two_supported_remote_type(self, mock):
        types = repo.get_git_remote_type()
        self.assertIn('github', types)
        self.assertIn('gitlab', types)

    @patch('gitissue.tools.repo.run_command', return_value='github.com\njira.com\ngitlab.com')
    def test_found_three_supported_remote_type(self, mock):
        types = repo.get_git_remote_type()
        self.assertIn('jira', types)
        self.assertIn('gitlab', types)
        self.assertIn('github', types)

    @patch('gitissue.tools.repo.run_command', return_value='')
    def test_no_supported_remote_type(self, mock):
        types = repo.get_git_remote_type()
        self.assertEqual([], types)


class TestSupportedRepos(TestCase):

    def test_valid_supported_repos(self):
        supported = ['gitlab', 'github', 'jira']
        self.assertEquals(supported, repo.get_supported_repos())


class TestGetRepoTypeFromUser(TestCase):

    @patch('builtins.input', return_value='jira')
    def test_correct_supported_repos_entered(self, mock):
        option = repo.get_repo_type_from_user()
        self.assertIn('jira', option)

    @patch('builtins.input', return_value='flowtastic')
    def test_incorrect_supported_repos_entered(self, mock):
        option = repo.get_repo_type_from_user()
        self.assertIn('ERROR:', option)
