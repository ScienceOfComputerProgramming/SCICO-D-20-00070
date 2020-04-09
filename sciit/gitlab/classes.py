import gitlab
import logging
import os
import re
import slugify
import sqlite3
import subprocess

from urllib.parse import urlparse

from git import Repo

from sciit import IssueRepo
from sciit.cli import ProgressTracker
from sciit.write_commit import GitCommitToIssue, create_new_issue

from sciit.regex import get_file_object_pattern, IssuePropertyRegularExpressions, add_comment_chars, \
    strip_comment_chars, get_issue_property_regex


class GitRepositoryIssueClient:

    def __init__(self, sciit_repository: IssueRepo):
        self._sciit_repository = sciit_repository

    def handle_issue(self, gitlab_issue, gitlab_sciit_issue_id_cache):
        gitlab_issue_id = gitlab_issue['iid']
        sciit_issue_id = gitlab_sciit_issue_id_cache.get_sciit_issue_id(gitlab_issue_id)

        if sciit_issue_id is not None:
            self.update_issue(sciit_issue_id, gitlab_issue)
        else:
            self.create_new_sciit_issue(gitlab_issue)

    def update_issue(self, sciit_issue_id, changes):
        gitlab_issue_id = changes['iid']

        sciit_issues = self._sciit_repository.get_all_issues()
        sciit_issue = sciit_issues[sciit_issue_id]

        latest_branch = sciit_issue.newest_issue_snapshot.in_branches[0]
        message = "Updates Issue %s (Gitlab Issue %d).\n\n(sciit issue update)" % \
                  (sciit_issue.issue_id, gitlab_issue_id)

        with GitCommitToIssue(self._sciit_repository, latest_branch, message) as commit_to_issue:
            new_sciit_issue_file_content = self.get_changed_file_content(sciit_issue, changes)

            with open(sciit_issue.working_file_path, 'w') as sciit_issue_file:
                sciit_issue_file.write(new_sciit_issue_file_content)

            commit_to_issue.file_paths.append(sciit_issue.file_path)

    def get_changed_file_content(self, sciit_issue, changes):

        comment_pattern = get_file_object_pattern(sciit_issue.file_path)

        with open(sciit_issue.working_file_path, 'r') as sciit_issue_file:
            file_content = sciit_issue_file.read()
            sciit_issue_content_in_file = file_content[sciit_issue.start_position:sciit_issue.end_position]

        sciit_issue_content, indent = strip_comment_chars(comment_pattern, sciit_issue_content_in_file)

        for key in ['title', 'due_date', 'weight', 'labels']:
            if key in changes:
                sciit_issue_content = self._update_single_line_property_in_file_content(
                    get_issue_property_regex(key), sciit_issue_content, key, changes[key])

        if 'description' in changes:
            sciit_issue_content = self._update_description_in_file_content(sciit_issue_content, changes['description'])

        sciit_issue_content = add_comment_chars(comment_pattern, sciit_issue_content, indent)

        return \
            file_content[0:sciit_issue.start_position] + \
            sciit_issue_content + \
            file_content[sciit_issue.end_position:]

    @staticmethod
    def _update_single_line_property_in_file_content(pattern, file_content, label, new_value):

        old_match = re.search(pattern, file_content)
        if old_match:
            old_start, old_end = old_match.span(1)
            return file_content[0:old_start] + new_value + file_content[old_end:]
        else:
            return file_content + f'\n@{label}{new_value}'

    @staticmethod
    def _update_description_in_file_content(file_content, new_value):

        old_match = re.search(IssuePropertyRegularExpressions.DESCRIPTION, file_content)
        if old_match:
            old_start, old_end = old_match.span(1)
            return file_content[0:old_start] + '\n' + new_value + file_content[old_end:]
        else:
            return file_content + f'\n@description\n{new_value}'

    def create_new_sciit_issue(self, gitlab_issue):
        create_new_issue(
            self._sciit_repository,
            gitlab_issue['title'],
            gitlab_issue['description'],
            commit_message="Creates New Issue %s (Gitlab Issue %d).\n\n(sciit issue update)" %
                           (gitlab_issue['title'], gitlab_issue['iid'])
        )


class GitlabIssueClient:

    def __init__(self, site_homepage, api_token):
        self._site_homepage = site_homepage
        self._api_token = api_token

    def handle_issues(self, project_path_with_namespace, sciit_issues, gitlab_sciit_issue_id_cache):
        with gitlab.Gitlab(self._site_homepage, self._api_token) as gitlab_instance:
            project = gitlab_instance.projects.get(project_path_with_namespace[1:])
            for sciit_issue in sciit_issues:
                sciit_issue_id = sciit_issue.issue_id
                gitlab_issue_id = gitlab_sciit_issue_id_cache.get_gitlab_issue_id(sciit_issue_id)

                if gitlab_issue_id is not None:
                    try:
                        gitlab_issue = project.issues.get(gitlab_issue_id)
                        self._update_gitlab_issue(gitlab_issue, sciit_issue)
                    except gitlab.GitlabGetError:
                        self._create_gitlab_issue(project, sciit_issue, gitlab_issue_id)

                else:
                    gitlab_issue = self._create_gitlab_issue(project, sciit_issue)
                    gitlab_issue_id = gitlab_issue.iid
                    gitlab_sciit_issue_id_cache.set_gitlab_issue_id(sciit_issue_id, gitlab_issue_id)

    @staticmethod
    def _create_gitlab_issue(project, sciit_issue, gitlab_issue_id=None):

        issue_data = dict()

        if gitlab_issue_id:
            issue_data['iid'] = gitlab_issue_id

        issue_data['created_at'] = sciit_issue.last_authored_date_string

        key_pairs = [('title', 'title'), ('description', 'description'), ('due_date', 'due_date')]

        for gitlab_key, sciit_key in key_pairs:
            if hasattr(sciit_issue, sciit_key):
                issue_data[gitlab_key] = getattr(sciit_issue, sciit_key)

        if 'title' not in issue_data or issue_data['title'] is None:
            issue_data['title'] = 'BLANK'

        if hasattr(sciit_issue, 'labels'):
            issue_data['labels'] = sciit_issue.labels

        return project.issues.create(issue_data)

    @staticmethod
    def _update_gitlab_issue(gitlab_issue, sciit_issue):
        change = False

        if gitlab_issue.title != sciit_issue.title and sciit_issue.title is not None:
            gitlab_issue.title = sciit_issue.title
            change = True

        if gitlab_issue.description != sciit_issue.description:
            gitlab_issue.description = sciit_issue.description
            change = True

        if gitlab_issue.labels != sciit_issue.labels:
            gitlab_issue.labels = sciit_issue.labels
            change = True

        major_status, minor_status = sciit_issue.status
        if major_status == 'Open' and gitlab_issue.state != 'opened':
            gitlab_issue.state_event = 'reopen'
            change = True
        elif major_status == 'Closed' and gitlab_issue.state != 'closed':
            gitlab_issue.state_event = 'close'
            change = True

        if change:
            gitlab_issue.updated_at = sciit_issue.last_authored_date_string
            gitlab_issue.save()

    def clear_issues(self, project_path_with_namespace):
        with gitlab.Gitlab(self._site_homepage, self._api_token) as gitlab_instance:
            project = gitlab_instance.projects.get(project_path_with_namespace[1:])
            for gitlab_issue in project.issues.list(all=True):
                gitlab_issue.delete()
                gitlab_issue.save()


class GitlabSciitIssueIDCache:

    def __init__(self, local_git_repository_path):
        self.local_git_repository_path = local_git_repository_path

    @property
    def _issue_id_cache_db_connection(self):
        issue_id_cache_db_path = self.local_git_repository_path + os.path.sep + '.git' + os.path.sep + \
                                 'issues' + os.path.sep + 'issue_id_cache.db'

        connection = sqlite3.connect(issue_id_cache_db_path)
        cursor = connection.cursor()

        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS issue_id_cache 
            (gitlab_issue_id INTEGER PRIMARY KEY, sciit_issue_id TEXT)
            WITHOUT ROWID
            '''
        )

        return connection

    def get_gitlab_issue_id(self, sciit_issue_id):
        query_string = 'SELECT gitlab_issue_id FROM issue_id_cache WHERE sciit_issue_id = ?'
        return self._get_issue_id(query_string, sciit_issue_id)

    def get_sciit_issue_id(self, gitlab_issue_id):
        query_string = 'SELECT sciit_issue_id FROM issue_id_cache WHERE gitlab_issue_id = ?'
        return self._get_issue_id(query_string, gitlab_issue_id)

    def _get_issue_id(self, query_string, other_issue_id):
        with self._issue_id_cache_db_connection as connection:
            cursor = connection.cursor()

            query_result = cursor.execute(query_string, (other_issue_id, )).fetchall()
            if len(query_result) > 0:
                return query_result[0][0]
            else:
                return None

    def set_gitlab_issue_id(self, sciit_issue_id, gitlab_issue_id):
        with self._issue_id_cache_db_connection as connection:
            cursor = connection.cursor()

            query_string = \
                '''
                INSERT INTO issue_id_cache
                VALUES (?, ?)
                '''

            cursor.execute(query_string, (gitlab_issue_id, sciit_issue_id))


class MirroredGitlabSciitProjectException(Exception):
        pass


class MirroredGitlabSciitProject:

    def __init__(self,
                 project_path_with_namespace, local_sciit_repository, gitlab_issue_client, gitlab_sciit_issue_id_cache):

        self.project_path_with_namespace = project_path_with_namespace
        self.local_sciit_repository = local_sciit_repository
        self.gitlab_issue_client = gitlab_issue_client
        self.gitlab_sciit_issue_id_cache = gitlab_sciit_issue_id_cache

        self.git_repository_issue_client = GitRepositoryIssueClient(self.local_sciit_repository)

    def reset_gitlab_issues(self, revision='--all', issue_ids=None):
        self.gitlab_issue_client.clear_issues(self.project_path_with_namespace)

        issue_history_iterator = self.local_sciit_repository.get_issue_history_iterator(revision, issue_ids)

        progress_tracker = ProgressTracker(True, len(issue_history_iterator), object_type_name='commits')

        for commit_hexsha_str, issues in issue_history_iterator:

            issues_to_be_updated = {issue for issue in issues.values() if issue.changed_by_commit(commit_hexsha_str)}
            self.gitlab_issue_client.handle_issues(
                self.project_path_with_namespace, issues_to_be_updated, self.gitlab_sciit_issue_id_cache)
            progress_tracker.processed_object()

    def process_web_hook_event(self, event, data):

        if event == 'Push Hook':
            self.handle_push_event(data)
        elif event == 'Issue Hook':
            self.handle_issue_event(data)

    def handle_push_event(self, data):

        self.local_sciit_repository.git_repository.git.execute(['git', 'pull', '--all'])
        self.local_sciit_repository.cache_issue_snapshots_from_unprocessed_commits()

        issue_history_iterator = self.local_sciit_repository.get_issue_history_iterator()

        latest_revisions_pattern = self._get_revision(data['before'], data['after'])

        git = self.local_sciit_repository.git_repository.git

        revision_list = git.execute(['git', 'rev-list', '--reverse', latest_revisions_pattern]).split('\n')

        for commit_hexsha_str, issues in issue_history_iterator:
            if commit_hexsha_str in revision_list:
                issues_to_be_updated = \
                    {issue for issue in issues.values() if issue.changed_by_commit(commit_hexsha_str)}

                self.gitlab_issue_client.handle_issues(
                    self.project_path_with_namespace, issues_to_be_updated, self.gitlab_sciit_issue_id_cache)

    def handle_issue_event(self, data):
        self.git_repository_issue_client.handle_issue(data['object_attributes'], self.gitlab_sciit_issue_id_cache)

    @staticmethod
    def _get_revision(before_commit_str, after_commit_str):
        if before_commit_str == '0000000000000000000000000000000000000000':
            return after_commit_str
        else:
            return f'{before_commit_str}..{after_commit_str}'


class GitlabTokenCache:

    def __init__(self, site_local_mirror_path):
        self._site_local_mirror_path = site_local_mirror_path

    @property
    def _gitlab_token_cache_db_connection(self):
        token_cache_db_path = self._site_local_mirror_path + os.sep + "gitlab_api_token_cache.db"

        connection = sqlite3.connect(token_cache_db_path)
        cursor = connection.cursor()

        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS gitlab_api_token_cache 
            (project_path_with_namespace TEXT PRIMARY KEY, api_token TEXT)
            WITHOUT ROWID
            '''
        )

        return connection

    def set_api_token(self, project_with_namespace, api_token):

        with self._gitlab_token_cache_db_connection as connection:

            cursor = connection.cursor()

            query_string = (
                '''
                REPLACE INTO gitlab_api_token_cache (project_path_with_namespace, api_token)
                VALUES(?, ?);

                '''
            )
            cursor.execute(query_string, (project_with_namespace, api_token))

    def get_api_token(self, project_path_with_namespace):

        with self._gitlab_token_cache_db_connection as connection:

            cursor = connection.cursor()

            query_string = (
                '''
                SELECT api_token FROM gitlab_api_token_cache
                WHERE project_path_with_namespace = ?
                '''
            )

            query_result = cursor.execute(query_string, (project_path_with_namespace,)).fetchall()
            if len(query_result) > 0:
                return query_result[0][0]
            else:
                return None


class MirroredGitlabSite:

    def __init__(self, site_homepage, site_local_mirror_path, gitlab_token_cache):
        self.site_homepage = site_homepage
        self.site_local_mirror_path = site_local_mirror_path

        self._gitlab_token_cache = gitlab_token_cache

        self.mirrored_gitlab_sciit_projects = dict()

    def set_gitlab_api_token(self, path_with_namespace, api_token):
        self._gitlab_token_cache.set_api_token(path_with_namespace, api_token)

    def get_mirrored_gitlab_sciit_project(self, path_with_namespace, local_git_repository_path=None):

        if path_with_namespace not in self.mirrored_gitlab_sciit_projects:

            _local_git_repository_path = local_git_repository_path if local_git_repository_path is not None \
                else self.site_local_mirror_path + path_with_namespace

            local_issue_repository = \
                self._configure_local_issue_repository(path_with_namespace, _local_git_repository_path)

            api_token = self._gitlab_token_cache.get_api_token(path_with_namespace)

            gitlab_issue_client = GitlabIssueClient(self.site_homepage, api_token)

            gitlab_sciit_issue_id_cache = GitlabSciitIssueIDCache(_local_git_repository_path)

            self.mirrored_gitlab_sciit_projects[path_with_namespace] = \
                MirroredGitlabSciitProject(
                    path_with_namespace, local_issue_repository, gitlab_issue_client, gitlab_sciit_issue_id_cache)

        return self.mirrored_gitlab_sciit_projects[path_with_namespace]

    def _configure_local_issue_repository(self, path_with_namespace, local_git_repository_path):

        git_url = self.make_git_url(path_with_namespace)

        if not os.path.exists(local_git_repository_path):
            subprocess.run(['git', 'clone', git_url, local_git_repository_path], check=True)
            git_repository = Repo(local_git_repository_path)
            local_issue_repository = IssueRepo(git_repository)
            local_issue_repository.setup_file_system_resources(install_hooks=False)
            local_issue_repository.cache_issue_snapshots_from_all_commits()
        else:
            git_repository = Repo(local_git_repository_path)
            local_issue_repository = IssueRepo(git_repository)
            local_issue_repository.cache_issue_snapshots_from_unprocessed_commits()

        return local_issue_repository

    def make_git_url(self, path_with_namespace):
        parsed_site_url = urlparse(self.site_homepage)
        git_url = f'git@{parsed_site_url.netloc}:{path_with_namespace}.git'
        return git_url


class MirroredGitlabSites:

    def __init__(self, sites_path):

        self.sites_path = sites_path

        self.mirrored_gitlab_sites = dict()

    def get_mirrored_gitlab_site(self, site_homepage):
        if site_homepage not in self.mirrored_gitlab_sites:

            site_directory_name = urlparse(site_homepage).netloc
            site_local_mirror_path = self.sites_path + os.path.sep + site_directory_name

            gitlab_token_cache = GitlabTokenCache(site_local_mirror_path)

            self.mirrored_gitlab_sites[site_homepage] = \
                MirroredGitlabSite(site_homepage, site_local_mirror_path, gitlab_token_cache)

        return self.mirrored_gitlab_sites[site_homepage]

    def get_mirrored_gitlab_sciit_project(self, site_homepage, path_with_namespace, local_git_repository_path=None):
        mirrored_gitlab_site = self.get_mirrored_gitlab_site(site_homepage)
        return mirrored_gitlab_site.get_mirrored_gitlab_sciit_project(path_with_namespace, local_git_repository_path)

