import json
import re
import logging

import dateutil.parser as dateparser
import requests


def create_issue_note(CONFIG, data, iid, note_type, last=None):
    """Creates a new issue note for gitlab issues
    """
    def activity_note(data, last=None):
        """Returns an activity note format
        """
        note = {}
        if last:
            note['body'] = f'closed on commit {data["commitsha"]} -- `SCIIT`'
        else:
            note['body'] = f'mentioned in commit {data["commitsha"]} -- `SCIIT`'
        note['created_at'] = data["date"]
        return note

    def revision_note(data):
        """Returns a revision note format   
        """
        if 'changes' not in data:
            return {}
        note = {}
        note['body'] = f'changes made to issue: {data["changes"]}'
        note['created_at'] = data["date"]
        return note

    if note_type == 'activity':
        note = activity_note(data, last)
    elif note_type == 'revision':
        note = revision_note(data)

    if note:

        logging.info(f'{note_type} added')
        url = f'{CONFIG.api_url}/projects/{CONFIG.project_id}/issues/{iid}/notes'
        requests.post(url,
                      headers={'Private-Token': CONFIG.api_token},
                      json=note)


def format_description(CONFIG, issue):
    output = issue['description']
    output += '\n\n\n`SCIIT locations`'
    for path in issue['filepaths']:
        output += f'\n* [{path["filepath"]} @{path["branch"]}]' + \
            f'({CONFIG.project_url}/blob/{path["branch"]}/{path["filepath"]})'
    return output


def create_issue(CONFIG, issue_data, multi_list):
    """Creates a new issue in gitlab
    """
    issue = {}
    issue['id'] = CONFIG.project_id
    issue['title'] = issue_data['title']
    if 'description' in issue_data:
        issue['description'] = format_description(CONFIG, issue_data)
    if 'label' in issue_data:
        issue['labels'] = issue_data['label']
    if 'due_date' in issue_data:
        issue['due_date'] = issue_data['due_date']
    issue['created_at'] = issue_data['created_date']

    r = requests.post(f'{CONFIG.api_url}/projects/{CONFIG.project_id}/issues',
                      headers={'Private-Token': CONFIG.api_token},
                      json=issue)
    if r.status_code == 201:
        iid = json.loads(r.content)['iid']
        multi_list.append((issue_data['id'], iid))

        # create notes for the issue based on commit activity and revisions
        for activity in issue_data['activity']:
            if len(issue_data['activity']) > 1:
                if activity == issue_data['activity'][0]:
                    create_issue_note(CONFIG, activity, iid,
                                      'activity', last=True)
                else:
                    create_issue_note(CONFIG, activity, iid, 'activity')
            else:
                create_issue_note(CONFIG, activity, iid, 'activity')
        for revision in issue_data['revisions']:
            create_issue_note(CONFIG, revision, iid, 'revision')

        # if closed during its history
        if issue_data['status'] == 'Closed':
            issue = {}
            issue['state_event'] = 'close'
            issue['updated_at'] = issue_data['activity'][0]['date']
            requests.put(f'{CONFIG.api_url}projects/{CONFIG.project_id}/issues/{iid}',
                         headers={'Private-Token': CONFIG.api_token},
                         json=issue)


def edit_issue(CONFIG, issue_data, pair):
    """Edits an issue in gitlab
    """
    # get issue from gitlab
    url = f'{CONFIG.api_url}projects/{CONFIG.project_id}/issues/{pair[1]}'
    gitlab_issue = requests.get(url, headers={
        'Private-Token': CONFIG.api_token})
    gitlab_issue = json.loads(gitlab_issue.content)

    # find changes to issue
    issue = {}
    if 'due_date' in issue_data:
        date = dateparser.parse(
            issue_data['due_date']).strftime('%Y-%m-%d')
    if gitlab_issue['title'] != issue_data['title']:
        issue['title'] = issue_data['title']
    if 'description' in issue_data:
        description = format_description(CONFIG, issue_data)
        if gitlab_issue['description'] != description:
            issue['description'] = description
    if 'label' in issue_data:
        if len(gitlab_issue['labels']) == 1:
            if gitlab_issue['labels'][0] != issue_data['label']:
                issue['labels'] = issue_data['label']
        elif ', '.join(gitlab_issue['label']) != issue_data['label']:
            issue['labels'] = issue_data['label']
    if 'due_date' in issue_data:
        if gitlab_issue['due_date'] != date:
            issue['due_date'] = issue_data['due_date']
    if gitlab_issue['state'] != 'closed':
        if issue_data['status'] == 'Closed':
            issue['state_event'] = 'close'
            issue['updated_at'] = issue_data['activity'][0]['date']

    # update issue if changed
    if issue:
        logging.info(f'{issue_data["id"]} has been updated')
        requests.put(url, headers={'Private-Token': CONFIG.api_token},
                     json=issue)

    # create notes for the issue based on commit activity and revisions
    for activity in issue_data['activity']:
        if len(issue_data['activity']) > 1:
            if activity == issue_data['activity'][0]:
                create_issue_note(CONFIG, activity, pair[1],
                                  'activity', last=True)
            else:
                create_issue_note(CONFIG, activity, pair[1], 'activity')
        else:
            create_issue_note(CONFIG, activity, pair[1], 'activity')
    for revision in issue_data['revisions']:
        create_issue_note(CONFIG, revision, pair[1], 'revision')
