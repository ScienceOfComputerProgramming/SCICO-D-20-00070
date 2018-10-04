import os
from unittest import TestCase
from unittest.mock import patch, MagicMock

from git import Commit
from git.util import hex_to_bin
from sciit import IssueSnapshot, IssueRepo
from sciit.errors import RepoObjectDoesNotExistError, RepoObjectExistsError
from tests.external_resources import safe_create_repo_dir, remove_existing_repo


class TestGetLocation(TestCase):

    def setUp(self):
        pass

    def test_something(self):
        pass

