import unittest

from unittest.mock import Mock, patch, mock_open

from sciit.gitlab.classes import GitRepositoryIssueClient

from sciit import Issue, IssueSnapshot

from sciit.read_commit import find_issues_in_blob
from sciit.regex import MARKDOWN


issue_file_content = """
---
@issue a-test-issue
@title A Test Issue
@labels not_triaged
@description
Test Issue Description.
---"""

modified_issue_file_content = """
---
@issue a-test-issue
@title A More Detailed Title for the Issue
@labels test_issue
@description
Test Issue Description with more details.
---"""


class TestGitRepositoryIssueClient(unittest.TestCase):

    def setUp(self):

        sciit_repository = Mock()

        self.git_repository_issue_client = GitRepositoryIssueClient(sciit_repository)

    def test_edit_issue(self):

        with patch('builtins.open', mock_open(read_data=issue_file_content)) as m:

            handle = m()

            commit = Mock()
            commit.repo.working_dir = "."

            data = find_issues_in_blob(MARKDOWN, issue_file_content)[0]

            data['file_path'] = 'dummy_repo/backlog/a-test-issue.md'

            all_issues = dict()

            issue_snapshot = IssueSnapshot(commit, data, in_branches=['master'])
            issue = Issue('a-test-issue', all_issues, {'master': commit})
            issue.add_snapshot(issue_snapshot)
            all_issues[issue.issue_id] = issue

            change_data = {
                'title': 'A More Detailed Title for the Issue',
                'description': 'Test Issue Description with more details.',
                'labels': 'test_issue'
            }

            self.git_repository_issue_client.update_issue(issue, change_data)

            handle.write.assert_called_once_with(modified_issue_file_content)


if __name__ == '__main__':
    unittest.main()

