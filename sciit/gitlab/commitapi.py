import json
import mimetypes
import re

import requests
from slugify import slugify
from sciit.regex import get_file_object_pattern, ISSUE
from sciit.gitlab.issueapi import format_description


class FileObject():
    path = None
    mime_type = None

    def __init__(self, path):
        self.path = path
        self.mime_type = mimetypes.guess_type(path)
        self.mime_type = self.mime_type[0]


def update_issue_source(issue, contents):

    file_object = FileObject(issue['filepath'])
    pattern = get_file_object_pattern(file_object)
    match_issue = re.findall(ISSUE.ID, contents)
    for match in match_issue:
        if slugify(match) == issue['id']:
            title_replace = f'(@[Ii]ssue[ _-]*(?:id|number|slug)* *[=:;>]*(?:{match})(?:.|[\r\n])*?(?:@[Ii]ssue[ _-])* *[Tt]itle *[=:;>]*)(.*)'
            description_replace = f'(@[Ii]ssue[ _-]*(?:id|number|slug)* *[=:;>]*(?:{match})(?:.|[\r\n])*?@(?:[Ii]ssue[ _-]*)*[Dd]escription *[=:;>]*)(.*(?:.|[\r\n])*?)(\n[\s]*@|$)'
            contents = re.sub(title_replace, r'\1' + issue['title'], contents)
            # TODO split the desciption lines by \n and add the # or *
            contents = re.sub(description_replace, r'\1' +
                              f'\n{issue["description"]}' + r'\3', contents)
    return contents


def create_commit(CONFIG, issue, commit):
    with open(CONFIG.gitlab_cache, 'r') as gl_cache:
        cache = json.loads(gl_cache.read())

    pair = [x for x in cache if x[1] == issue['iid']]

    if pair:
        history = CONFIG.repo.build_history()
        old_issue = history[pair[0][0]]
        new_issue = old_issue
        new_issue['title'] = issue['title']
        new_issue['description'] = format_description(CONFIG, new_issue)
        remove_formatting = re.compile(
            r'(?:\n\n\n)*`SCIIT locations`(?:.*(?:.|[\r\n])*)')
        if new_issue['description'] != issue['description']:
            new_issue['description'] = remove_formatting.sub(
                '', issue['description'])
            new_issue['description'] = format_description(CONFIG, new_issue)
            new_issue['description'] = remove_formatting.sub(
                '', new_issue['description'])
        else:
            new_issue['description'] = remove_formatting.sub(
                '', new_issue['description'])
    else:
        new_issue = issue
        del new_issue['iid']

    if 'filepath' in new_issue:
        # update file with new commit info
        commit['branch'] = list(new_issue['open_in'])[0]
        commit['commit_message'] = f'Updating issue \'{new_issue["title"]}\''
        r = requests.get(f'{CONFIG.project_url}/raw/{commit["branch"]}/{new_issue["filepath"]}', headers={
            'Private-Token': CONFIG.api_token})
        source = r.content.decode()
        updated_source = update_issue_source(new_issue, source)

        commit['actions'] = [
            {"action": "update",
             "file_path": new_issue['filepath'],
             "content": updated_source}
        ]
    else:
        # create a file with this issue info
        content = 'content'
        commit['branch'] = 'master'
        commit['commit_message'] = f'Creating issue \'{new_issue["title"]}\''
        commit['actions'] = [
            {"file_path": 'issues.txt',
             "content": content}
        ]
        r = requests.get(f'{CONFIG.project_url}/raw/master/issues.txt', headers={
            'Private-Token': CONFIG.api_token})
        if r.status_code == 404:
            commit['actions'][0]['action'] = 'create'
        else:
            commit['actions'][0]['action'] = 'update'

    r = requests.post(f'{CONFIG.api_url}/projects/{CONFIG.project_id}/repository/commits', headers={
        'Private-Token': CONFIG.api_token}, json=commit)
    pass
