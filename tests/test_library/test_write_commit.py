import unittest

from unittest.mock import Mock, patch, mock_open

from sciit.write_commit import close_issue


class TestWriteCommit(unittest.TestCase):

    def test_close_issue(self):

        with \
                patch('sciit.write_commit.git_commit_to_issue', new_callable=Mock()) as git_commit_to_issue_mock, \
                patch('builtins.open', mock_open(read_data="dabce")) as open_func_mock:

            issue_repository = Mock()

            git_commit_issue_manager_mock = Mock()
            git_commit_issue_manager_mock.__enter__ = Mock()
            git_commit_issue_manager_mock.__exit__ = Mock()
            git_commit_to_issue_mock.return_value = git_commit_issue_manager_mock

            file_handle_mock = open_func_mock()

            issue = Mock()
            issue.file_path = "issue.md"
            issue.start_position = 1
            issue.end_position = 4

            close_issue(issue_repository, issue, branch_names=['master'])

            file_handle_mock.write.assert_called_once_with("de")


if __name__ == '__main__':
    unittest.main()
