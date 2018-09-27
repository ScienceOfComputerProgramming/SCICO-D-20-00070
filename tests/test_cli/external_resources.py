import re
from tests.external_resources import safe_create_repo_dir
from sciit import IssueRepo, IssueCommit, IssueTree, Issue
from sciit.functions import write_last_issue
from git import Commit
from git.util import hex_to_bin

safe_create_repo_dir('here')
repo = IssueRepo('here')

first_data = [{'id': '1', 'title': 'the contents of the file', 'filepath': 'path',
               'description': 'This issue had a description'},
              {'id': '2', 'title': 'the contents of the file', 'filepath': 'path'},
              {'id': '3', 'title': 'the contents of the file', 'filepath': 'path'},
              {'id': '4', 'title': 'the contents of the file', 'filepath': 'path'},
              {'id': '5', 'title': 'the contents of the file', 'filepath': 'path'},
              {'id': '6',
               'title': 'The title of your issue',
               'description': 'A description of you issue as you\n'
               + 'want it to be ``markdown`` supported',
               'assignees': 'nystrome, kevin, daniels',
               'due_date': '12 oct 2018',
               'label': 'in-development',
               'weight': '4',
               'priority': 'high',
               'filepath': 'README.md'}]

second_data = [{'id': '1', 'title': 'the contents of the file', 'filepath': 'path'},
               {'id': '2', 'title': 'the contents of the file',
                'filepath': 'path'},
               {'id': '9', 'title': 'the contents of the file',
                'filepath': 'path'},
               {'id': '6', 'title': 'the contents of the file', 'filepath': 'path',
                'description': 'description has changed'},
               {'id': '12', 'title': 'the contents of the file', 'filepath': 'path',
                'description': 'here is a nice description'}]

first_issues = [Issue.create_from_data(repo, d) for d in first_data]
first_issue_tree = IssueTree.create_from_issues(repo, first_issues)

second_issues = [Issue.create_from_data(repo, d) for d in second_data]
second_issue_tree = IssueTree.create_from_issues(repo, second_issues)

first_sha = '43e8d11ec2cb9802151533ae8d9c5dcc5dec91a4'
second_sha = '622918a4c6539f853320e06804f73d1165df69d0'
third_sha = '7a13fb71dfc40675176ce28b8ad6df9132039711'

first_commit = Commit(repo, hex_to_bin(first_sha))
second_commit = Commit(repo, hex_to_bin(second_sha))
third_commit = Commit(repo, hex_to_bin(third_sha))

first_issue_commit = IssueCommit.create(repo, first_commit, first_issue_tree)
second_issue_commit = IssueCommit.create(repo, second_commit, second_issue_tree)

write_last_issue(repo.issue_dir, second_sha)

ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
