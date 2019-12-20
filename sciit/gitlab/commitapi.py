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


----

import logging
import os
import shutil
import sqlite3
import stat
import subprocess


from queue import LifoQueue
from threading import Thread


from git import Repo
from gitlab import Gitlab


from datetime import datetime, timedelta

from flask import Response

from sciit import IssueRepo


class GitlabIssueClient:

    def __init__(self, api_url, api_token, mirrored_gitlab_site):
        self.api_url = api_url
        self.api_token = api_token

        self.mirrored_gitlab_site = mirrored_gitlab_site
        self.server_address = api_url[8:api_url.index('/', 8)]

    def handle_issue_snapshot(self, project_id, issue_snapshot):
        self._handle_issue_snapshots(project_id, [issue_snapshot])

    def _handle_issue_snapshots(self, project_id, issue_snapshots):
        with Gitlab(self.api_url, self.api_token) as gitlab_instance:
            project = gitlab_instance.projects.get(project_id)

            mirrored_gitlab_issue_repository = \
                self.mirrored_gitlab_site.get_mirrored_gitlab_issue_repository(project.name)

            for issue_snapshot in issue_snapshots:
                sciit_issue_id = issue_snapshot.issue_id
                gitlab_issue_id = mirrored_gitlab_issue_repository.get_gitlab_issue_id(project_id, sciit_issue_id)

                if gitlab_issue_id is not None:
                    gitlab_issue = project.issues.get(gitlab_issue_id)
                    self._update_gitlab_issue(gitlab_issue, issue_snapshot)

                else:
                    gitlab_issue = self._create_gitlab_issue(project, issue_snapshot)
                    gitlab_issue_id = gitlab_issue.iid
                    mirrored_gitlab_issue_repository.set_gitlab_issue_id(project_id, sciit_issue_id, gitlab_issue_id)

    @staticmethod
    def _create_gitlab_issue(project, sciit_issue):
        issue_data = {
            'title': sciit_issue.title,
            'description': sciit_issue.description
        }
        return project.issues.create(issue_data)

    @staticmethod
    def _update_gitlab_issue(gitlab_issue, sciit_issue):
        if gitlab_issue.title != sciit_issue.title:
            gitlab_issue.title = sciit_issue.title
        if gitlab_issue.description != sciit_issue.description:
            gitlab_issue.description = sciit_issue.description
        gitlab_issue.save()

    def clear_gitlab_issues(self, project_id):
        with Gitlab(self.api_url, self.api_token) as gitlab_instance:
            project = gitlab_instance.projects.get(project_id)

            for gitlab_issue in project.issues.list():
                gitlab_issue.delete()
                gitlab_issue.save()


class MirroredGitLabSciitRepository:

    def __init__(self, remote_project_url, local_git_repository_path):
        self.remote_project_url = remote_project_url
        self.local_git_repository_path = local_git_repository_path

        self._local_issue_repository = None

    @property
    def local_issue_repository(self):
        self._ensure_local_issue_repository_exists()
        return self._local_issue_repository

    def _ensure_local_issue_repository_exists(self, force=False):

        if force:
            def onerror(func, path, _):
                os.chmod(path, stat.S_IWUSR)
                func(path)

            shutil.rmtree(self.local_git_repository_path, onerror=onerror)
            self._local_issue_repository = None

        if not os.path.exists(self.local_git_repository_path):
            subprocess.run(
                ['git', 'clone', '--mirror', self.remote_project_url, self.local_git_repository_path], check=True)

        if self._local_issue_repository is None:
            git_repository = Repo(path=self.local_git_repository_path)
            self._local_issue_repository = IssueRepo(git_repository)
            self._local_issue_repository.cache_issue_snapshots_from_all_commits()

    @property
    def _issue_id_cache_db_connection(self):
        issue_id_cache_db_path = \
            self.local_git_repository_path + os.path.sep + 'issues' + os.path.sep + 'issue_id_cache.db'

        connection = sqlite3.connect(issue_id_cache_db_path)
        cursor = connection.cursor()

        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS issue_id_cache (gitlab_issue_id TEXT, sciit_issue_id INTEGER) WITHOUT ROWID
            '''
        )

        return connection

    def get_gitlab_issue_id(self, sciit_issue_id):
        with self._issue_id_cache_db_connection as connection:
            cursor = connection.cursor()

            query_string = \
                '''
                SELECT gitlab_issue_id
                FROM issue_id_cache
                WHERE sciit_issue_id = ?
                '''

            query_result = cursor.execute(query_string, (sciit_issue_id, )).fetchall()
            return query_result[0][0]

    def set_gitlab_issue_id(self, sciit_issue_id, gitlab_issue_id):
        with self._issue_id_cache_db_connection as connection:
            cursor = connection.cursor()

            query_string = \
                '''
                INSERT INTO issue_id_cache
                VALUES (?, ?)
                '''

            query_result = cursor.execute(query_string, (sciit_issue_id, gitlab_issue_id)).fetchall()
            return query_result[0][0]

    def find_issue_snapshots(self, revision=None):
        self.local_issue_repository.git_repository.git.execute(['git', 'fetch', '--all'])
        self.local_issue_repository.cache_issue_snapshots_from_unprocessed_commits()
        return self.local_issue_repository.find_issue_snapshots(revision)


class MirroredGitlabSciitProject:

    def __init__(self, project_id, gitlab_issue_client, mirrored_gitlab_issue_repository):

        self.project_id = project_id
        self.gitlab_issue_client = gitlab_issue_client
        self.mirrored_gitlab_issue_repository = mirrored_gitlab_issue_repository

        self.last_push_hook_event_timestamp = None
        self.last_issue_hook_event_timestamp = None

    def reset_gitlab_issues(self):
        self.gitlab_issue_client.clear_issues(self.project_id)
        issue_snapshots = self.mirrored_gitlab_issue_repository.find_issue_snapshots()
        self.gitlab_issue_client.handle_issue_snapshots(self.project_id, issue_snapshots)

    def _push_web_hook_event_resulted_from_issue_web_hook_event(self):
        if not self.last_issue_hook_event_timestamp:
            return False
        else:
            delta = self.last_push_hook_event_timestamp - self.last_issue_hook_event_timestamp
            return delta < timedelta(seconds=10)

    def _issue_web_hook_event_resulted_from_push_web_hook_event(self):
        if not self.last_push_hook_event_timestamp:
            return False
        else:
            delta = self.last_issue_hook_event_timestamp - self.last_push_hook_event_timestamp
            return delta < timedelta(seconds=10)

    def process_web_hook_event(self, event, data):

        if event == 'Push Hook':
            self.last_push_hook_event_timestamp = datetime.now()

            if self._push_web_hook_event_resulted_from_issue_web_hook_event():
                return Response({'status': 'Rejected', 'message': 'This request originated from an Issue Hook'})

            else:
                return self.handle_push_event(data)

        elif event == 'Issue Hook':

            self.last_issue_hook_event_timestamp = datetime.now()

            if self._issue_web_hook_event_resulted_from_push_web_hook_event():
                return Response({'status': 'Rejected', 'message': 'This request originated from a Push Hook.'})

            else:
                return self.handle_issue_event(data)
        else:
            return Response({'status': 'Failure', 'message': f'Gitlab hook - {event} not supported'}, status=404)

    def handle_push_event(self, data):
        project_id = data['id']
        revision = self._get_revision(data['before'], data['after'])
        issue_snapshots = self.mirrored_gitlab_issue_repository.find_issue_snapshots(revision)

        self.gitlab_issue_client.handle_issue_snapshots(issue_snapshots)

    def _get_revision(self, before, after):



class MirroredGitlabSite:

    def __init__(self, site_local_mirror_path):
        self.site_local_mirror_path = site_local_mirror_path

        self.mirrored_gitlab_sciit_projects = dict()

    def get_mirrored_gitlab_sciit_project(self, project_id, project_url, api_url, project_name):

        if project_id not in self.mirrored_gitlab_sciit_projects:

            local_git_repository_path = self.site_local_mirror_path + os.path.sep + project_name

            mirrored_gitlab_issue_repository = \
                MirroredGitLabSciitRepository(project_url, local_git_repository_path)

            api_token = self._get_gitlab_api_token(project_id)

            gitlab_issue_client = GitlabIssueClient(api_url, api_token, self)

            self.mirrored_gitlab_sciit_projects[project_id] = \
                MirroredGitlabSciitProject(project_id, mirrored_gitlab_issue_repository)

        return self.mirrored_gitlab_sciit_projects[project_id]

    def get_mirrored_gitlab_repository(self, project_name):
        return self.mirrored_gitlab_sciit_projects.get(project_name).mirrored_gitlab_issue_repository

    @staticmethod
    def _get_gitlab_api_token(remote_project_url):
        if 'GITLAB_API_TOKEN' in os.environ:
            return os.environ['GITLAB_API_TOKEN']
        else:
            return '8b9W5ZAkDCsvJYQzhJZ2'


class GitLabWebHookReceiver:

    def __init__(self, sites_path):

        self.sites_path = sites_path

        self.configure_logger_for_web_service_events()

        self.mirrored_gitlab_sites = dict()

        self.issue_update_pipes = dict()

    def initialise_web_hook_for_gitlab_project(self, data):

        repository_homepage = data['repository']['homepage']

        if repository_homepage not in self.mirrored_gitlab_sites:

            site_directory_name = repository_homepage[8:repository_homepage.index('/', 8)]
            site_path = self.sites_path + os.path.sep + site_directory_name

            self.mirrored_gitlab_sites[repository_homepage] = MirroredGitlabSite(site_path)

        mirrored_gitlab_site = self.mirrored_gitlab_sites[repository_homepage]

        project_id = data['project']['id']
        project_url = data['project']['web_url']
        api_url = data['repository']['homepage'].rsplit('/', 1)[0].rsplit('/', 1)[0] + '/api/v4/'
        project_name = data['project']['name']

        return mirrored_gitlab_site.get_mirrored_gitlab_sciit_project(project_id, project_url, api_url, project_name)

    def configure_logger_for_web_service_events(self):

        logging.basicConfig(
            format='%(levelname)s:[%(asctime)s]cl %(message)s',
            datefmt='%m/%d/%Y %I:%M:%S %p',
            filename=self.sites_path + os.path.sep + 'sciit-gitlab.log',
            level=logging.INFO
        )
