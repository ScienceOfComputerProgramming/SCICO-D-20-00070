# -*- coding: utf-8 -*-

"""
Functions needed to launch the gitlab webservice. Note that this webservice cannot run together with the local git sciit
 web interface.
"""

import logging

from queue import LifoQueue
from threading import Thread
from urllib.parse import urlparse

from flask import Flask, Response, request, json

from .classes import MirroredGitlabSites


app = Flask(__name__)


sciit_web_hook_username = 'twsswt'  # 'sciit_web_hook'


mirrored_gitlab_sites = None

job_queue = None


def get_project_information(data):
    parsed_uri = urlparse(data['repository']['homepage'])
    site_homepage = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
    path_with_namespace = parsed_uri.path
    return site_homepage, path_with_namespace


def no_new_commits(data):
    for commit in data['commits']:
        if '(sciit issue update)' not in commit['message']:
            return False
    return True


@app.route('/', methods=['POST'])
def index():
    """
    The single endpoint of the service handling all incoming web hooks.
    """

    event = request.headers.environ['HTTP_X_GITLAB_EVENT']
    logging.info(f'received a {event} event.')

    data = request.get_json()

    if event == 'Push Hook' and no_new_commits(data):
        return Response(
            {'status': 'Rejected', 'message': 'Event originated from a previous sciit issue web hook action.'})
    elif event == 'Issue Hook' and data['user']['username'] == sciit_web_hook_username:
        return Response(
            {'status': 'Rejected', 'message': 'Event originated from a previous sciit push web hook action.'})
    else:
        site_homepage, path_with_namespace = get_project_information(data)
        # def _job():
        mirrored_gitlab_sciit_project = mirrored_gitlab_sites.get_mirrored_gitlab_sciit_project(site_homepage, path_with_namespace)
        logging.info(f'using local repository: {mirrored_gitlab_sciit_project.local_git_repository_path}.')
        mirrored_gitlab_sciit_project.process_web_hook_event(event, data)

        # job_queue.put(_job)
        return Response({'status': 'Accepted'})


@app.route('/status', methods=['GET'])
def status():
    """
    An endpoint to check the status of the webservice to determine its running state without making any changes.
    """
    global job_queue
    global mirrored_gitlab_sites

    response_data = {
        'job_queue': len(job_queue),
        'projects': len(mirrored_gitlab_sites.mirrored_gitlab_sites),
        "status": "running",
         "message": "The SCIIT-GitLab integration service is operational."
    }
    return Response(json.dumps(response_data))


@app.route('/init', methods=['POST'])
def init():
    """
    An endpoint that can be used to initialise the local sciit repository.
    """

    global job_queue
    global mirrored_gitlab_sites

    data = request.get_json()

    site_homepage, path_with_namespace = get_project_information(data)

    mirrored_gitlab_sites.get_mirrored_gitlab_sciit_project(site_homepage, path_with_namespace)

    project_url = data['project']['web_url']
    response_data = {
        'status': 'Success',
        'message': f'Issue cache initialised for project {project_url}.',
    }
    return Response(json.dumps(response_data))


def configure_global_resources(project_dir_path):
    """
    A helper function that launches the web service.
    """
    global mirrored_gitlab_sites
    global job_queue

    job_queue = LifoQueue()
    mirrored_gitlab_sites = MirroredGitlabSites(project_dir_path)

    def process_jobs():
        while True:
            job = job_queue.get(block=True)
            job()

    Thread(target=process_jobs).start()


if __name__ == '__main__':
    default_args = type('args', (), {})
    default_args.project_dir_path = ''
    configure_global_resources(default_args)
    app.run(host='0.0.0.0', port=5000)
else:
    configure_global_resources('./gitlab-sites')
