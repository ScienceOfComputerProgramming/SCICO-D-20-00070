import unittest

from git import Repo

from sciit.gitlab.classes import GitlabIssueClient, GitlabSciitIssueIDCache, GitlabTokenCache,\
    MirroredGitlabSciitProject, MirroredGitlabSites
from sciit import IssueRepo

import os


class TestMirroredGitlabSciitProject(unittest.TestCase):

    def setUp(self):

        local_sites_path = '../../../'
        local_git_repository_path = '../../'
        site_homepage = 'https://git.dcs.gla.ac.uk'
        path_with_namespace = 'twsswt/sciit-gitlab-test'

        mirrored_gitlab_sites = MirroredGitlabSites(local_sites_path)

        self.mirrored_gitlab_sciit_project = \
            mirrored_gitlab_sites.get_mirrored_gitlab_sciit_project(
                site_homepage, path_with_namespace, local_git_repository_path)

    def test_reset_gitlab_issues(self):

        # revision = '37072584d1d4ff5ba9faebbefc84f9d6ab063741~1' + '..' + 'HEAD'
        # issue_ids = ['add-accept-functionality-to-new-issue-command']

        self.mirrored_gitlab_sciit_project.reset_gitlab_issues()


if __name__ == '__main__':
    unittest.main()
