# -*- coding: utf-8 -*-
"""Module that contains the functions needed create commits from
handling issue hooks.

:@author: Nystrom Edwards
:Created: 16 August 2018
"""
import json
import mimetypes
import os
import re
import logging

import requests
from slugify import slugify

from sciit.gitlab.issueapi import format_description
from sciit.regex import (C_STYLE, HASKELL, HTML, IssuePropertyRegularExpressions, MATLAB, PLAIN, PYTHON,
                         get_file_object_pattern)


class FileObject():
    """Object wrapper to use for getting file object pattern
    """
    path = None
    mime_type = None

    def __init__(self, path):
        self.path = path
        self.mime_type = mimetypes.guess_type(path)
        self.mime_type = self.mime_type[0]


def get_leading_char(pattern):
    """Returns the character that is used at the begining of the block comment
    based on the pattern
    """
    if pattern in (PYTHON, HTML, MATLAB, HASKELL):
        return ''
    elif pattern == C_STYLE:
        return '*'
    elif pattern == PLAIN:
        return '#'


def update_issue_source(issue, contents):
    """Updates the source code block description content based on the
    issue that was changed
    """
    if 'filepath' in issue:
        file_object = FileObject(issue['filepath'])
    else:
        issue['id'] = slugify(issue['title'])
        file_object = FileObject('issues.txt')
    pattern = get_file_object_pattern(file_object)
    match_issue = re.findall(IssuePropertyRegularExpressions.ID, contents)

    # iterate through the matches and change the details of the particular issue
    for i, match in enumerate(match_issue):
        if slugify(match) == issue['id']:

            # if match found with this id then replace the tilte and description changed
            title_replace = f'(@[Ii]ssue[ _-]*(?:id|number|slug)* *[=:;>]*(?:{match})(?:.|[\r\n])*?(?:@[Ii]ssue[ _-])* *[Tt]itle *[=:;>]*)(.*)'
            description_replace = f'(@[Ii]ssue[ _-]*(?:id|number|slug)* *[=:;>]*(?:{match})(?:.|[\r\n])*?@(?:[Ii]ssue[ _-]*)*[Dd]escription *[=:;>]*)(.*(?:.|[\r\n])*?)((?:.*$)|(?:.*@|$))'
            description_padding = f'([\t| ]+)@(?:[Ii]ssue[ _-]*)*[Dd]escription'
            description_padding = re.findall(description_padding, contents)
            if description_padding:
                description_padding = description_padding[i]

            # check the file pattern to add leading char
            leading_char = get_leading_char(pattern)
            issue['description'] = re.sub(
                f'\n', f'\n{leading_char}{description_padding} ', issue['description'])

            # replace the title and description based on what the user entered
            contents = re.sub(title_replace, r'\1' + issue['title'], contents)
            contents = re.sub(description_replace, r'\1' +
                              f'\n{leading_char}{description_padding} {issue["description"]}\n' +
                              r'\3', contents)

    logging.info('Updated source code file')
    contents = contents.replace('[] ', '')
    return contents


def create_commit(CONFIG, issue, commit):
    """Create the commit in gitlab with the issue information
    """

    # determine issue existence
    if os.path.exists(CONFIG.gitlab_cache):
        with open(CONFIG.gitlab_cache, 'r') as gl_cache:
            cache = json.loads(gl_cache.read())
            pair = [x for x in cache if x[1] == issue['iid']]
            logging.info('Cache exists')
    else:
        pair = []
        cache = []
        logging.info('No cache exists')

    # clean the format from gitlab
    remove_formatting = re.compile(
        r'(?:\n\n\n)*`SCIIT locations`(?:.*(?:.|[\r\n])*)')

    # use existing issue information if issue exists in cache
    if pair:
        history = CONFIG.repo.build_history()
        old_issue = history[pair[0][0]]
        new_issue = old_issue
        new_issue['title'] = issue['title']
        new_issue['description'] = format_description(CONFIG, new_issue)
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

    # check if issue belongs to a file
    if 'filepath' in new_issue:
        # update file with new commit info
        commit['branch'] = list(new_issue['open_in'])[0]
        commit['commit_message'] = f'Updating issue \'{new_issue["title"]}\''
        r = requests.get(f'{WEBSERVICE_CONFIG.project_url}/raw/{commit["branch"]}/{new_issue["filepath"]}', headers={
            'Private-Token': CONFIG.api_token})
        source = r.content.decode()
        updated_source = update_issue_source(new_issue, source)

        # set commit actions
        commit['actions'] = [
            {"action": "update",
             "file_path": new_issue['filepath'],
             "content": updated_source}
        ]
    # if it does not belong to a file
    else:

        commit['branch'] = 'master'
        commit['commit_message'] = f'Creating issue \'{new_issue["title"]}\''
        commit['actions'] = [
            {"file_path": 'issues.txt'}
        ]

        # check for issues.txt existance in gitlab.com on master
        r = requests.get(f'{WEBSERVICE_CONFIG.project_url}/raw/master/issues.txt', headers={
            'Private-Token': CONFIG.api_token})

        # if issues.txt does not exist
        if r.status_code == 404:
            # create a file with this issue info
            new_issue['description'] = remove_formatting.sub(
                '', issue['description'])
            content = f'#***\n# @issue {slugify(new_issue["title"])}\n' + \
                f'# @title {new_issue["title"]}\n' + \
                f'# @description\n' + \
                f'{new_issue["description"]}\n' + \
                f'#***'
            content = update_issue_source(new_issue, content)
            commit['actions'][0]['content'] = content
            commit['actions'][0]['action'] = 'create'
            logging.info('Creating new issues.txt file')

        # if issues.txt exists
        else:
            # and issue in the cache
            if pair:
                # update the issue existing in issues.txt
                source = r.content.decode()
                updated_source = update_issue_source(new_issue, source)
                commit['actions'][0]['content'] = updated_source
                commit['actions'][0]['action'] = 'update'

            # and issue not in the cache
            else:
                # add new issue to issues.txt
                source = r.content.decode()
                new_issue['description'] = remove_formatting.sub(
                    '', issue['description'])
                source += f'\n\n#***\n# @issue {slugify(new_issue["title"])}\n' + \
                    f'# @title {new_issue["title"]}\n' + \
                    f'# @description\n' + \
                    f'{new_issue["description"]}\n' + \
                    f'#***'
                updated_source = update_issue_source(new_issue, source)
                commit['actions'][0]['content'] = updated_source
                commit['actions'][0]['action'] = 'update'

    # create commit
    r = requests.post(f'{WEBSERVICE_CONFIG.api_url}/projects/{WEBSERVICE_CONFIG.project_id}/repository/commits', headers={
        'Private-Token': CONFIG.api_token}, json=commit)
    logging.info(f'commit created on {WEBSERVICE_CONFIG.path}')

    # save issue to cache if it was not there
    if not pair:
        cache.append((issue['id'], issue['iid']))
        with open(CONFIG.gitlab_cache, 'w') as gl_cache:
            gl_cache.write(json.dumps(cache))
            logging.info(f'New entry in cache {issue["id"]}')
