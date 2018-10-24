# -*- coding: utf-8 -*-
"""
Functions needed to launch the gitlab webservice. Note that this webservice cannot run together with the local git sciit
 web interface.
"""

import json
import os
import subprocess
import logging

from flask import Flask, Response, request
from git import Repo
from datetime import datetime, timezone, timedelta

from sciit import IssueRepo
from sciit.cli.color import ColorPrint
from sciit.gitlab.pushhook import handle_push_event
from sciit.gitlab.issuehook import handle_issue_event

app = Flask(__name__)


class WEBSERVICE_CONFIG:
    repo = None
    api_token = None
    api_url = None
    project_id = None
    project_url = None
    path = None
    gitlab_cache = None
    last_push_hook = None
    last_issue_hook = None


def configure_logger_for_web_service_events():
    global WEBSERVICE_CONFIG

    logging.basicConfig(
        format='%(levelname)s:[%(asctime)s]cl %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p',
        filename=WEBSERVICE_CONFIG.path + '.log',
        level=logging.INFO
    )


@app.route('/', methods=['POST'])
def index():
    """
    The single endpoint of the service handling all incoming webhooks.
    """
    global WEBSERVICE_CONFIG

    data = request.get_json()

    # Set configuration items
    WEBSERVICE_CONFIG.api_token = os.environ['GITLAB_API_TOKEN']
    WEBSERVICE_CONFIG.api_url = data['repository']['homepage'].rsplit('/', 1)[0].rsplit('/', 1)[0] + '/api/v4/'
    WEBSERVICE_CONFIG.project_id = data['project']['id']
    WEBSERVICE_CONFIG.project_url = data['project']['web_url']
    WEBSERVICE_CONFIG.path = data['project']['url'].rsplit('/', 1)[1]
    WEBSERVICE_CONFIG.gitlab_cache = WEBSERVICE_CONFIG.path + '.cache'
    event = request.headers.environ['HTTP_X_GITLAB_EVENT']

    configure_logger_for_web_service_events()

    # Download, build and set issue repository
    if WEBSERVICE_CONFIG.repo is None or not os.path.exists(WEBSERVICE_CONFIG.path):
        if os.path.exists(WEBSERVICE_CONFIG.path):
            git_repository = Repo(WEBSERVICE_CONFIG.path)
            WEBSERVICE_CONFIG.repo = IssueRepo(git_repository)
        else:
            subprocess.run(['git', 'clone', '--mirror', data['project']['url'], WEBSERVICE_CONFIG.path], check=True)
            git_repository = Repo(WEBSERVICE_CONFIG.path)
            WEBSERVICE_CONFIG.repo = IssueRepo(git_repository)
            WEBSERVICE_CONFIG.repo.cache_issue_snapshots_from_all_commits()

    logging.info(f'received a {event} event')
    logging.info(f'using repository: {WEBSERVICE_CONFIG.path}')

    if event == 'Push Hook':

        WEBSERVICE_CONFIG.last_push_hook = datetime.now(timezone.utc)
        if WEBSERVICE_CONFIG.last_issue_hook:
            delta = WEBSERVICE_CONFIG.last_push_hook - WEBSERVICE_CONFIG.last_issue_hook
            if delta < timedelta(seconds=10):
                return json.dumps({"status": "Rejected",
                                   "message": "This request originated from an IssueSnapshot Hook"})
            else:
                return handle_push_event(WEBSERVICE_CONFIG, data)
        else:
            return handle_push_event(WEBSERVICE_CONFIG, data)

    elif event == 'IssueSnapshot Hook':

        WEBSERVICE_CONFIG.last_issue_hook = datetime.now(timezone.utc)
        if WEBSERVICE_CONFIG.last_push_hook:
            delta = WEBSERVICE_CONFIG.last_issue_hook - WEBSERVICE_CONFIG.last_push_hook
            if delta < timedelta(seconds=10):
                return json.dumps({"status": "Rejected",
                                   "message": "This request originated from an Push Hook"})
            else:
                return handle_issue_event(WEBSERVICE_CONFIG, data)
        else:
            return handle_issue_event(WEBSERVICE_CONFIG, data)
    else:
        return Response({"status": "Failue", "message": f"Gitlab hook - {event} not supported"}, status=404)


@app.route('/status', methods=['GET'])
def status():
    """
    An endpoint to check the status of the webservice to determine its running state without making any changes
    """
    return json.dumps({"status": "running", "message": "The SCIIT-GitLab integration service is operational"})


@app.route('/init', methods=['POST'])
def init():
    """
    An endpoint that can be used to initialise the sciit repository
    """
    global WEBSERVICE_CONFIG
    data = request.get_json()

    if WEBSERVICE_CONFIG.repo is None or os.path.exists(WEBSERVICE_CONFIG.path):
        import stat
        import shutil

        def onerror(func, path, excp_info):
            os.chmod(path, stat.S_IWUSR)
            func(path)
        shutil.rmtree(WEBSERVICE_CONFIG.path, onerror=onerror)

    subprocess.run(['git', 'clone', '--mirror', data['remote'], WEBSERVICE_CONFIG.path], check=True)
    git_repository = Repo(path=WEBSERVICE_CONFIG.path)
    WEBSERVICE_CONFIG.repo = IssueRepo(git_repository)
    WEBSERVICE_CONFIG.repo.cache_issue_snapshots_from_all_commits()

    return json.dumps({"status": "Success", "message": f"{data['remote']} IssueSnapshot Repository Initialized"})


def launch(args):
    """
    A helper function that launches the webservice from sciit cli
    """
    global WEBSERVICE_CONFIG
    WEBSERVICE_CONFIG.repo = args.repo

    if 'GITLAB_API_TOKEN' in os.environ:
        WEBSERVICE_CONFIG.api_token = os.environ['GITLAB_API_TOKEN']
        app.run(host='0.0.0.0', port=5000)
    else:
        ColorPrint.bold_red(
            'Must specify gitlab api access token as environment variable')
        ColorPrint.bold('Set token to environment variable GITLAB_API_TOKEN')
        exit(127)


if __name__ == '__main__':
    args = type('args', (), {})
    args.repo = None
    launch(args)
