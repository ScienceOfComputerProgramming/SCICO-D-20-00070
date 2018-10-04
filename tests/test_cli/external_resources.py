import datetime
import re
from tests.external_resources import create_mock_git_repository, create_mock_commit, \
    create_mock_commit_with_issue_snapshots, create_mock_parents
from sciit import IssueRepo, Issue

first_data = [{'issues[id': '1', 'title': 'the contents of the file', 'filepath': 'path',
               'description': 'This issue had a description'},
              {'issues[id': '2', 'title': 'the contents of the file', 'filepath': 'path'},
              {'issues[id': '3', 'title': 'the contents of the file', 'filepath': 'path'},
              {'issues[id': '4', 'title': 'the contents of the file', 'filepath': 'path'},
              {'issues[id': '5', 'title': 'the contents of the file', 'filepath': 'path'},
              {'issues[id': '6',
               'title': 'The title of your issue',
               'description': 'A description of you issue as you\n'
               + 'want it to be ``markdown`` supported',
               'assignees': 'nystrome, kevin, daniels',
               'due_date': '12 oct 2018',
               'label': 'in-development',
               'weight': '4',
               'priority': 'high',
               'filepath': 'README.md'}]

second_data = [{'issues[id': '1', 'title': 'the contents of the file', 'filepath': 'path'},
               {'issues[id': '2', 'title': 'the contents of the file',
                'filepath': 'path'},
               {'issues[id': '9', 'title': 'the contents of the file',
                'filepath': 'path'},
               {'issues[id': '6', 'title': 'the contents of the file', 'filepath': 'path',
                'description': 'description has changed'},
               {'issues[id': '12', 'title': 'the contents of the file', 'filepath': 'path',
                'description': 'here is a nice description'}]

first_commit, first_issue_snapshots = create_mock_commit_with_issue_snapshots(
    '43e8d11ec2cb9802151533ae8d9c5dcc5dec91a4',
    'Nystrome',
    datetime.datetime(2018, 1, 1),
    first_data,
)

second_commit, second_issue_snapshots = create_mock_commit_with_issue_snapshots(
    '622918a4c6539f853320e06804f73d1165df69d0',
    'Nystrome',
    datetime.datetime(2018, 1, 1),
    second_data,
    create_mock_parents(first_commit)
)

third_commit = create_mock_commit('7a13fb71dfc40675176ce28b8ad6df9132039711', 'Nystrome', datetime.datetime(2018, 1, 1))

mock_git_repository = \
    create_mock_git_repository('here', [('master', second_commit)], [third_commit, second_commit, first_commit])

repo = IssueRepo(mock_git_repository)

issues = [None] * 13

issues[1] = Issue('1')
issues[1].update(first_issue_snapshots[0])
issues[1].open_in.add('master')
issues[1].update(second_issue_snapshots[0])

issues[2] = Issue('2')
issues[2].update(first_issue_snapshots[1])
issues[2].open_in.add('master')
issues[2].update(second_issue_snapshots[1])

issues[3] = Issue('3')
issues[3].update(first_issue_snapshots[2])

issues[4] = Issue('4')
issues[4].update(first_issue_snapshots[3])

issues[5] = Issue('5')
issues[5].update(first_issue_snapshots[4])

issues[6] = Issue('6')
issues[6].update(first_issue_snapshots[5])
issues[6].open_in.add('master')
issues[6].update(second_issue_snapshots[3])

issues[9] = Issue('9')
issues[9].update(second_issue_snapshots[3])
issues[9].open_in.add('master')

issues[12] = Issue('12')
issues[12].update(second_issue_snapshots[4])
issues[12].open_in.add('master')


ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
