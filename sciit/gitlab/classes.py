import logging
import os
import sqlite3
import subprocess

from git import Repo
from gitlab import Gitlab, GitlabGetError

from sciit import IssueRepo
from sciit.cli import ProgressTracker


class GitlabIssueClient:

    def __init__(self, site_homepage, api_token):
        self.site_homepage = site_homepage
        self.api_token = api_token

    def handle_issues(self, project_path_with_namespace, sciit_issues, gitlab_sciit_issue_id_cache):
        with Gitlab(self.site_homepage, self.api_token) as gitlab_instance:
            project = gitlab_instance.projects.get(project_path_with_namespace)
            for sciit_issue in sciit_issues:
                sciit_issue_id = sciit_issue.issue_id
                gitlab_issue_id = gitlab_sciit_issue_id_cache.get_gitlab_issue_id(sciit_issue_id)

                if gitlab_issue_id is not None:
                    try:
                        gitlab_issue = project.issues.get(gitlab_issue_id)
                        self._update_gitlab_issue(gitlab_issue, sciit_issue)
                    except GitlabGetError:
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
        with Gitlab(self.site_homepage, self.api_token) as gitlab_instance:
            project = gitlab_instance.projects.get(project_path_with_namespace)
            for gitlab_issue in project.issues.list(all=True):
                gitlab_issue.delete()
                gitlab_issue.save()


class GitlabSciitIssueIDCache:

    def __init__(self, local_git_repository_path):
        self.local_git_repository_path = local_git_repository_path

    @property
    def _issue_id_cache_db_connection(self):
        issue_id_cache_db_path = \
            self.local_git_repository_path + os.sep + '.git' + os.path.sep + 'issues' + os.path.sep + 'issue_id_cache.db'

        connection = sqlite3.connect(issue_id_cache_db_path, )
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
        with self._issue_id_cache_db_connection as connection:
            cursor = connection.cursor()

            query_string = \
                '''
                SELECT gitlab_issue_id
                FROM issue_id_cache
                WHERE sciit_issue_id = ?
                '''

            query_result = cursor.execute(query_string, (sciit_issue_id, )).fetchall()
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

    def __init__(self, project_path_with_namespace, gitlab_issue_client, local_sciit_repository, gitlab_sciit_issue_id_cache):

        self.project_path_with_namespace = project_path_with_namespace
        self.gitlab_issue_client = gitlab_issue_client
        self.local_sciit_repository = local_sciit_repository
        self.gitlab_sciit_issue_id_cache = gitlab_sciit_issue_id_cache

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
        revision = self._get_revision(data['before'], data['after'])

        self.local_sciit_repository.git_repository.git.execute(['git', 'fetch', '--all'])
        self.local_sciit_repository.cache_issue_snapshots_from_unprocessed_commits()

        issue_snapshots = self.local_sciit_repository.find_issue_snapshots(revision)

        self.gitlab_issue_client.handle_issue_snapshots(self.project_path_with_namespace, issue_snapshots)

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

    def get_gitlab_api_token(self, project_path_with_namespace):

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

    def get_mirrored_gitlab_sciit_project(self, path_with_namespace, local_git_repository_path=None):

        if path_with_namespace not in self.mirrored_gitlab_sciit_projects:

            _local_git_repository_path = \
                local_git_repository_path if local_git_repository_path is not None \
                else self.site_local_mirror_path + os.path.sep + path_with_namespace

            project_url = self.site_homepage + '/' + path_with_namespace

            if not os.path.exists(_local_git_repository_path):
                subprocess.run(
                    ['git', 'clone', '--mirror', project_url, _local_git_repository_path], check=True)

            git_repository = Repo(_local_git_repository_path)
            local_issue_repository = IssueRepo(git_repository)
            # TODO
            # local_issue_repository.cache_issue_snapshots_from_all_commits()
            #
            api_token = self._gitlab_token_cache.get_gitlab_api_token(path_with_namespace)

            gitlab_issue_client = GitlabIssueClient(self.site_homepage, api_token)

            gitlab_sciit_issue_id_cache = GitlabSciitIssueIDCache(_local_git_repository_path)

            self.mirrored_gitlab_sciit_projects[path_with_namespace] = \
                MirroredGitlabSciitProject(
                    path_with_namespace, gitlab_issue_client, local_issue_repository, gitlab_sciit_issue_id_cache)

        return self.mirrored_gitlab_sciit_projects[path_with_namespace]


class MirroredGitlabSites:

    def __init__(self, sites_path):

        self.sites_path = sites_path

        self.configure_logger_for_web_service_events()

        self.mirrored_gitlab_sites = dict()

    def get_mirrored_gitlab_sciit_project(self, site_homepage, path_with_namespace, local_git_repository_path=None):
        if site_homepage not in self.mirrored_gitlab_sites:

            site_directory_name = site_homepage[8:site_homepage.index('/', 8)]
            site_local_mirror_path = self.sites_path + os.path.sep + site_directory_name

            gitlab_token_cache = GitlabTokenCache(site_local_mirror_path)

            self.mirrored_gitlab_sites[site_homepage] = \
                MirroredGitlabSite(site_homepage, site_local_mirror_path, gitlab_token_cache)

        mirrored_gitlab_site = self.mirrored_gitlab_sites[site_homepage]

        return mirrored_gitlab_site.get_mirrored_gitlab_sciit_project(path_with_namespace, local_git_repository_path)

    def configure_logger_for_web_service_events(self):

        logging.basicConfig(
            format='%(levelname)s:[%(asctime)s]cl %(message)s',
            datefmt='%m/%d/%Y %I:%M:%S %p',
            filename=self.sites_path + os.path.sep + 'sciit-gitlab.log',
            level=logging.INFO
        )
