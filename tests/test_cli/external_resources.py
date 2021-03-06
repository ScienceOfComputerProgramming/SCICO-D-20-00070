import datetime
import re
from tests.external_resources import create_mock_git_repository, create_mock_commit, \
    create_mock_commit_with_issue_snapshots, create_mock_parents
from sciit import IssueRepo, Issue

first_data = [{'issue_id': '1', 'title': 'the contents of the file', 'file_path': 'path',
               'description': 'This issue had a description'},
              {'issue_id': '2', 'title': 'the contents of the file', 'file_path': 'path'},
              {'issue_id': '3', 'title': 'the contents of the file', 'file_path': 'path'},
              {'issue_id': '4', 'title': 'the contents of the file', 'file_path': 'path'},
              {'issue_id': '5', 'title': 'the contents of the file', 'file_path': 'path'},
              {'issue_id': '6',
               'title': 'The title of your issue',
               'description': 'A description of you issue as you\n'
               + 'want it to be ``markdown`` supported',
               'assignees': 'nystrome, kevin, daniels',
               'due_date': '12 oct 2018',
               'label': 'in-development',
               'weight': '4',
               'priority': 'high',
               'file_path': 'README.md'}]

second_data = [{'issue_id': '1', 'title': 'the contents of the file', 'file_path': 'path'},
               {'issue_id': '2', 'title': 'the contents of the file',
                'file_path': 'path'},
               {'issue_id': '9', 'title': 'the contents of the file',
                'file_path': 'path'},
               {'issue_id': '6', 'title': 'the contents of the file', 'file_path': 'path',
                'description': 'description has changed'},
               {'issue_id': '12', 'title': 'the contents of the file', 'file_path': 'path',
                'description': 'here is a nice description'}]

first_commit, first_issue_snapshots = create_mock_commit_with_issue_snapshots(
    '43e8d11ec2cb9802151533ae8d9c5dcc5dec91a4',
    'Nystrome',
    datetime.datetime(2018, 1, 1),
    first_data,
)

heads_at_first_commit = {'master': '43e8d11ec2cb9802151533ae8d9c5dcc5dec91a4'}

second_commit, second_issue_snapshots = create_mock_commit_with_issue_snapshots(
    '622918a4c6539f853320e06804f73d1165df69d0',
    'Nystrome',
    datetime.datetime(2018, 1, 1),
    second_data,
    create_mock_parents(first_commit)
)

heads_at_second_commit = {'master': '622918a4c6539f853320e06804f73d1165df69d0'}

third_commit = create_mock_commit('7a13fb71dfc40675176ce28b8ad6df9132039711', 'Nystrome', datetime.datetime(2018, 1, 1))

issues = dict()

issues['1'] = Issue('1', issues, heads_at_second_commit)
issues['1'].add_snapshot(first_issue_snapshots[0])
issues['1'].open_in_branches.add('master')
issues['1'].add_snapshot(second_issue_snapshots[0])

issues['2'] = Issue('2', issues, heads_at_second_commit)
issues['2'].add_snapshot(first_issue_snapshots[1])
issues['2'].open_in_branches.add('master')
issues['2'].add_snapshot(second_issue_snapshots[1])

issues['3'] = Issue('3', issues, heads_at_second_commit)
issues['3'].add_snapshot(first_issue_snapshots[2])

issues['4'] = Issue('4', issues, heads_at_second_commit)
issues['4'].add_snapshot(first_issue_snapshots[3])

issues['5'] = Issue('5', issues, heads_at_second_commit)
issues['5'].add_snapshot(first_issue_snapshots[4])

issues['6'] = Issue('6', issues, heads_at_second_commit)
issues['6'].add_snapshot(first_issue_snapshots[5])
issues['6'].open_in_branches.add('master')
issues['6'].add_snapshot(second_issue_snapshots[3])

issues['9'] = Issue('9', issues, heads_at_second_commit)
issues['9'].add_snapshot(second_issue_snapshots[3])
issues['9'].open_in_branches.add('master')

issues['12'] = Issue('12', issues, heads_at_second_commit)
issues['12'].add_snapshot(second_issue_snapshots[4])
issues['12'].open_in_branches.add('master')


ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
