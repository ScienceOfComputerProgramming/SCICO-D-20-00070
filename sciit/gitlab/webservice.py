# -*- coding: utf-8 -*-

"""
Functions needed to launch the gitlab webservice. Note that this webservice cannot run together with the local git sciit
 web interface.
"""

import logging

from urllib.parse import urlparse

from flask import Flask, Response, request, json
from werkzeug.exceptions import BadRequest

from .classes import MirroredGitlabSites


app = Flask(__name__)


mirrored_gitlab_sites = None


def get_project_site_homepage_and_path_with_namespace(data):
    parsed_uri = urlparse(data['repository']['homepage'])
    site_homepage = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
    path_with_namespace = parsed_uri.path
    return site_homepage, path_with_namespace


def invalid_issue_hook(data, gitlab_username):
    return 'user' not in data or \
           'username' not in data['user'] or \
           data['user']['username'] == gitlab_username


def invalid_push_hook(data):
    if 'commits' not in data:
        return True
    else:
        for commit in data['commits']:
            if '(sciit issue update)' not in commit['message']:
                return False
        return True


@app.route('/', methods=['POST'])
def index():
    """
    The single endpoint of the service handling all incoming web hooks.
    """

    data = request.get_json()

    if not(
            'repository' in data and
            'homepage' in data['repository'] and
            'HTTP_X_GITLAB_EVENT' in request.headers.environ
    ):
        raise BadRequest()

    site_homepage, path_with_namespace = get_project_site_homepage_and_path_with_namespace(data)

    mirrored_gitlab_sciit_project = \
        mirrored_gitlab_sites.get_mirrored_gitlab_sciit_project(site_homepage, path_with_namespace)

    sciit_web_hook_secret_token = mirrored_gitlab_sciit_project.web_hook_secret_token

    if 'HTTP_X_GITLAB_TOKEN' not in request.headers.environ or \
            request.headers.environ['HTTP_X_GITLAB_TOKEN'] != sciit_web_hook_secret_token:
        return Response(json.dumps({'status': 'Rejected', 'message': 'Invalid Gitlab token'}))

    event = request.headers.environ['HTTP_X_GITLAB_EVENT']
    logging.info(f'Received {event} event.')

    if event == 'Push Hook' and invalid_push_hook(data):
        logging.info("Rejecting push event that originated from sciit issue change.")
        return Response(
            {'status': 'Rejected', 'message': 'Event originated from a previous sciit issue web hook action.'})

    elif event == 'Issue Hook' and invalid_issue_hook(data, mirrored_gitlab_sciit_project.gitlab_username):

        logging.info("Rejecting issue event that originated from sciit commit.")
        return Response(
            {'status': 'Rejected', 'message': 'Event originated from a previous sciit push web hook action.'})
    else:
        logging.info(f'Using local repository[{mirrored_gitlab_sciit_project.path_with_namespace}].')
        mirrored_gitlab_sciit_project.process_web_hook_event(event, data)

        return Response({'status': 'Accepted'})


@app.route('/status', methods=['GET'])
def status():
    """
    An endpoint to check the status of the webservice to determine its running state without making any changes.
    """
    response_data = {
        "status": "running",
        "message": "The SCIIT-GitLab integration service is operational."
    }
    return Response(json.dumps(response_data))


def configure_global_resources(project_dir_path):

    global mirrored_gitlab_sites
    mirrored_gitlab_sites = MirroredGitlabSites(project_dir_path)


def launch_standalone(args):
    configure_global_resources(default_args)
    app.run(host='0.0.0.0', port=5000)


if __name__ == '__main__':
    default_args = type('args', (), {})
    default_args.project_dir_path = '.'
    launch_standalone(default_args)
else:
    configure_global_resources('./gitlab-sites')
