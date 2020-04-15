# -*- coding: utf-8 -*-

"""
Entry point for the Gitlab Integration Service
"""

import logging
import random
import string

from gitlab import Gitlab, GitlabGetError, GitlabAuthenticationError
from urllib.parse import urlparse

from flask import Flask, Response, request, json, render_template
from werkzeug.exceptions import BadRequest

from .classes import MirroredGitlabSites


app = Flask(__name__)


mirrored_gitlab_sites = None


def get_project_site_homepage_and_path_with_namespace(url):
    parsed_url = urlparse(url)

    if parsed_url.netloc == b'' or parsed_url.netloc == '' or parsed_url.path == b'':
        return None, None

    site_homepage = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_url)
    path_with_namespace = parsed_url.path
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

    site_homepage, path_with_namespace = \
        get_project_site_homepage_and_path_with_namespace(data['repository']['homepage'])

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


@app.route("/configure", methods=['POST', 'GET'])
def configure():
    """
    Page for showing the content and history of an issue, derived from its repository commits.
    """

    gitlab_project_url = request.form.get('gitlab-project-url')
    gitlab_username = request.form.get('gitlab-username')
    gitlab_api_token = request.form.get('gitlab-api-token')

    response_data = {
        'gitlab-project-url': gitlab_project_url if gitlab_project_url is not None else '',
        'gitlab-username': gitlab_username if gitlab_username is not None else ''
    }

    if gitlab_project_url is None and gitlab_username is None and gitlab_api_token is None:
        return render_template('configure.html', data=response_data)

    site_homepage, path_with_namespace = get_project_site_homepage_and_path_with_namespace(gitlab_project_url)

    if site_homepage is None or path_with_namespace is None:
        response_data['result'] = 'failure'
        response_data['message'] = "You don't appear to have provided a valid URL for your project."

        return render_template('configure.html', data=response_data)

    end_point_url = request.url[0:-10]

    with Gitlab(site_homepage, gitlab_api_token) as gitlab_api:
        try:
            project = gitlab_api.projects.get(path_with_namespace[1:])
            hooks = project.hooks.list()

            for hook in hooks:
                hook_url = hook.attributes['url']

                if hook_url == end_point_url:
                    hook.delete()

            web_hook_token = ''.join(random.choice(string.ascii_letters) for i in range(10))

            project.hooks.create({
                'url': end_point_url,
                'push_events': True,
                'issues_events': True,
                'token': web_hook_token
            })

            global mirrored_gitlab_sites

            mirrored_gitlab_site = mirrored_gitlab_sites.get_mirrored_gitlab_site(site_homepage)
            mirrored_gitlab_site.set_credentials(path_with_namespace, gitlab_username, web_hook_token, gitlab_api_token)

            response_data['result'] = 'success'

            return render_template('configure.html', data=response_data)

        except (GitlabGetError, GitlabAuthenticationError):
            response_data['result'] = 'failure'
            response_data['message'] = "Couldn't connect to the Gitlab API using the given URL and access token."
            return render_template('configure.html', data=response_data)


def configure_global_resources(project_dir_path):

    global mirrored_gitlab_sites
    mirrored_gitlab_sites = MirroredGitlabSites(project_dir_path)


def launch_standalone(args):
    configure_global_resources('./gitlab-sites')
    app.run(host='0.0.0.0', port=5000, debug=True)


if __name__ == '__main__':
    default_args = type('args', (), {})
    default_args.project_dir_path = '.'
    launch_standalone(default_args)
else:
    configure_global_resources('./gitlab-sites')
