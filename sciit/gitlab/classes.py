import gitlab
import os
import sqlite3
import subprocess

from urllib.parse import urlparse

from git import Repo

from sciit import IssueRepo, Issue
from sciit.cli import ProgressTracker
from sciit.write_commit import create_issue as create_sciit_issue, update_issue as update_sciit_issue, \
    close_issue as close_sciit_issue


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


class GitRepositoryIssueClient:

    def __init__(self, sciit_repository: IssueRepo):
        self._sciit_repository = sciit_repository

    def handle_issue(self, gitlab_issue, gitlab_sciit_issue_id_cache):

        gitlab_issue_id = gitlab_issue['iid']
        sciit_issue_id = gitlab_sciit_issue_id_cache.get_sciit_issue_id(gitlab_issue_id)
        action = gitlab_issue['action']

        if sciit_issue_id is not None:
            sciit_issues = self._sciit_repository.get_all_issues()
            sciit_issue = sciit_issues[sciit_issue_id]

            if action == 'close':
                self.close_issue(sciit_issue)
            else:
                self.update_issue(sciit_issue, gitlab_issue)

        else:
            sciit_issue_id = self.create_new_issue(gitlab_issue)
            gitlab_sciit_issue_id_cache.set_gitlab_issue_id(sciit_issue_id, gitlab_issue_id)

    def update_issue(self, sciit_issue, gitlab_issue):

        _changes = dict()

        for key in ['title', 'due_date', 'weight', 'labels']:
            if key in gitlab_issue:
                change_value = gitlab_issue[key] if bool(gitlab_issue[key]) else ''

                if not (getattr(sciit_issue, key) is None and change_value == ''):
                    _new_value = self._format_gitlab_property_value_for_sciit(key, change_value)
                    _changes[key] = _new_value

        if 'description' in gitlab_issue and not (gitlab_issue['description'] == '' and
                                                  sciit_issue.description is None):
            _changes['description'] = gitlab_issue['description']

        git_commit_message = \
            "Updates Issue %s (Gitlab Issue %d).\n\n(sciit issue update)" % \
                (sciit_issue.issue_id, gitlab_issue['iid'])

        update_sciit_issue(self._sciit_repository, sciit_issue, _changes, git_commit_message, push=True)

    @staticmethod
    def _format_gitlab_property_value_for_sciit(label, value):
        if isinstance(value, str):
            return value
        elif label == 'labels':
            return ", ".join([l['title'] for l in value])
        else:
            return str(value)

    def create_new_issue(self, gitlab_issue):

        message = "Creates New Issue %s (Gitlab Issue %d).\n\n(sciit issue update)" % \
                               (gitlab_issue['title'], gitlab_issue['iid'])

        title = gitlab_issue['title']

        data = dict()
        for key in ['due_date', 'weight', 'labels', 'description']:
            if key in gitlab_issue and bool(gitlab_issue[key]):
                data[key] = self._format_gitlab_property_value_for_sciit(key, gitlab_issue[key])

        return create_sciit_issue(self._sciit_repository, title, data, git_commit_message=message, push=True)

    def close_issue(self, sciit_issue: Issue) -> None:
        close_sciit_issue(self._sciit_repository, sciit_issue, push=True)


class _TemporaryProjectVisibility:

    def __init__(self, project, visibility):
        self._project = project
        self._temporary_visibility = visibility

        self._original_visibility = None

    def __enter__(self):
        self._original_visibility = self._project.visibility
        self._project.visibility = self._temporary_visibility
        self._project.save()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._project.visibility = self._original_visibility
        self._project.save()


def temporary_visibility(project, visibility):
    return _TemporaryProjectVisibility(project, visibility)


class GitlabIssueClient:

    def __init__(self, site_homepage, api_token):
        self._site_homepage = site_homepage
        self._api_token = api_token

    def handle_issues(self, path_with_namespace, sciit_issues,
                      gitlab_sciit_issue_id_cache: GitlabSciitIssueIDCache):

        with gitlab.Gitlab(self._site_homepage, self._api_token) as gitlab_instance:
            project = gitlab_instance.projects.get(path_with_namespace[1:])
            with temporary_visibility(project, 'private'):
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

    def clear_issues(self, path_with_namespace):
        with gitlab.Gitlab(self._site_homepage, self._api_token) as gitlab_instance:
            project = gitlab_instance.projects.get(path_with_namespace[1:])

            with temporary_visibility(project, 'private'):
                for gitlab_issue in project.issues.list(all=True):
                    gitlab_issue.delete()
                    gitlab_issue.save()


class MirroredGitlabSciitProjectException(Exception):
        pass


class MirroredGitlabSciitProject:

    def __init__(self,
                 path_with_namespace,
                 local_git_repository_path,
                 git_url,
                 gitlab_username,
                 web_hook_secret_token,
                 gitlab_issue_client):

        self.path_with_namespace = path_with_namespace
        self.gitlab_issue_client = gitlab_issue_client
        self.gitlab_username = gitlab_username
        self.web_hook_secret_token = web_hook_secret_token

        self._configure_local_issue_repository(local_git_repository_path, git_url)

        self.gitlab_sciit_issue_id_cache = GitlabSciitIssueIDCache(local_git_repository_path)

        self.git_repository_issue_client = GitRepositoryIssueClient(self.local_sciit_repository)

    def reset_gitlab_issues(self, revision='--all', issue_ids=None):

        self.local_sciit_repository.synchronize_with_remotes()

        self.gitlab_issue_client.clear_issues(self.path_with_namespace)

        issue_history_iterator = self.local_sciit_repository.get_issue_history_iterator(revision, issue_ids)

        progress_tracker = ProgressTracker(len(issue_history_iterator), object_type_name='commits')

        for commit_hexsha_str, issues in issue_history_iterator:

            issues_to_be_updated = {issue for issue in issues.values() if issue.changed_by_commit(commit_hexsha_str)}
            self.gitlab_issue_client.handle_issues(
                self.path_with_namespace, issues_to_be_updated, self.gitlab_sciit_issue_id_cache)
            progress_tracker.processed_object()

    def process_web_hook_event(self, event, data):

        if event == 'Push Hook':
            self.handle_push_event(data)
        elif event == 'Issue Hook':
            self.handle_issue_event(data)

    @property
    def local_git_repository(self):
        return self.local_sciit_repository.git_repository

    def _configure_local_issue_repository(self, local_git_repository_path, git_url):

        if not os.path.exists(local_git_repository_path):
            subprocess.run(['git', 'clone', git_url, local_git_repository_path], check=True)
            git_repository = Repo(local_git_repository_path)
            self.local_sciit_repository = IssueRepo(git_repository)
            self.local_sciit_repository.setup_file_system_resources(install_hooks=False)
            self.local_sciit_repository.synchronize_with_remotes()
            self.local_sciit_repository.cache_issue_snapshots_from_all_commits()
        else:
            git_repository = Repo(local_git_repository_path)
            self.local_sciit_repository = IssueRepo(git_repository)
            # self.local_sciit_repository.synchronize_with_remotes()
            # self.local_sciit_repository.cache_issue_snapshots_from_unprocessed_commits()

    def handle_push_event(self, data):

        self.local_sciit_repository.synchronize_with_remotes()

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
                    self.path_with_namespace, issues_to_be_updated, self.gitlab_sciit_issue_id_cache)

    def handle_issue_event(self, data):
        self.git_repository_issue_client.handle_issue(data['object_attributes'], self.gitlab_sciit_issue_id_cache)

    @staticmethod
    def _get_revision(before_commit_str, after_commit_str):
        if before_commit_str == '0000000000000000000000000000000000000000':
            return after_commit_str
        else:
            return f'{before_commit_str}..{after_commit_str}'


class GitlabCredentialsCache:

    def __init__(self, site_local_mirror_path):
        self._site_local_mirror_path = site_local_mirror_path

    @property
    def _gitlab_credentials_db_connection(self):
        token_cache_db_path = self._site_local_mirror_path + os.sep + "gitlab_credentials.db"

        connection = sqlite3.connect(token_cache_db_path)
        cursor = connection.cursor()

        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS GitlabCredentials 
            (
             project_path_with_namespace TEXT PRIMARY KEY,
             gitlab_username TEXT,
             web_hook_secret_token TEXT,
             api_token TEXT
            )
            WITHOUT ROWID
            '''
        )

        return connection

    def set_credentials(self, project_with_namespace, gitlab_username, web_hook_secret_token, api_token):

        with self._gitlab_credentials_db_connection as connection:

            cursor = connection.cursor()

            query_string = (
                '''
                REPLACE INTO GitlabCredentials (
                 project_path_with_namespace,
                 gitlab_username,
                 web_hook_secret_token,
                 api_token
                )
                VALUES(?, ?, ?, ?);

                '''
            )
            cursor.execute(query_string, (project_with_namespace, gitlab_username, web_hook_secret_token, api_token))

    def get_credentials(self, project_path_with_namespace):

        with self._gitlab_credentials_db_connection as connection:

            cursor = connection.cursor()

            query_string = (
                '''
                SELECT gitlab_username, web_hook_secret_token, api_token FROM GitlabCredentials
                WHERE project_path_with_namespace = ?
                '''
            )

            query_result = cursor.execute(query_string, (project_path_with_namespace,)).fetchall()
            if len(query_result) > 0:
                return query_result[0][0], query_result[0][1], query_result[0][2]
            else:
                return None


class MirroredGitlabSite:

    def __init__(self, site_homepage, site_local_mirror_path, gitlab_credentials):
        self.site_homepage = site_homepage
        self.site_local_mirror_path = site_local_mirror_path

        self._gitlab_credentials = gitlab_credentials

        self.mirrored_gitlab_sciit_projects = dict()

    def set_credentials(self, path_with_namespace, gitlab_username, web_hook_secret_token, api_token):
        self._gitlab_credentials.set_credentials(path_with_namespace, gitlab_username, web_hook_secret_token, api_token)

    def get_mirrored_gitlab_sciit_project(self, path_with_namespace, local_git_repository_path=None):

        if path_with_namespace not in self.mirrored_gitlab_sciit_projects:

            _local_git_repository_path = local_git_repository_path if local_git_repository_path is not None \
                else self.site_local_mirror_path + path_with_namespace

            gitlab_username, web_hook_secret_token, api_token = \
                self._gitlab_credentials.get_credentials(path_with_namespace)

            gitlab_issue_client = GitlabIssueClient(self.site_homepage, api_token)

            git_url = self.make_git_url(path_with_namespace, gitlab_username, api_token)

            self.mirrored_gitlab_sciit_projects[path_with_namespace] = \
                MirroredGitlabSciitProject(
                    path_with_namespace, _local_git_repository_path, git_url, gitlab_username, web_hook_secret_token,
                    gitlab_issue_client)

        return self.mirrored_gitlab_sciit_projects[path_with_namespace]

    def make_git_url(self, path_with_namespace, gitlab_username, personal_access_token):
        parsed_site_url = urlparse(self.site_homepage)
        git_url = f'https://{gitlab_username}:{personal_access_token}@{parsed_site_url.netloc}{path_with_namespace}.git'
        return git_url


class MirroredGitlabSites:

    def __init__(self, sites_path):

        self.sites_path = sites_path

        self.mirrored_gitlab_sites = dict()

    def get_mirrored_gitlab_site(self, site_homepage):
        if site_homepage not in self.mirrored_gitlab_sites:

            site_directory_name = urlparse(site_homepage).netloc
            site_local_mirror_path = self.sites_path + os.path.sep + site_directory_name
            os.makedirs(site_local_mirror_path, exist_ok=True)

            gitlab_credentials_cache = GitlabCredentialsCache(site_local_mirror_path)

            self.mirrored_gitlab_sites[site_homepage] = \
                MirroredGitlabSite(site_homepage, site_local_mirror_path, gitlab_credentials_cache)

        return self.mirrored_gitlab_sites[site_homepage]

    def get_mirrored_gitlab_sciit_project(self, site_homepage, path_with_namespace, local_git_repository_path=None):
        mirrored_gitlab_site = self.get_mirrored_gitlab_site(site_homepage)
        return mirrored_gitlab_site.get_mirrored_gitlab_sciit_project(path_with_namespace, local_git_repository_path)
