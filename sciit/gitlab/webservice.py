# -*- coding: utf-8 -*-
"""Module that contains the functions needed to lauch the gitlab
webservice. Note that this webservice cannot run together with
the local git sciit web interface

:@author: Nystrom Edwards
:Created: 07 August 2018
"""
import json
import os
import subprocess
import logging
import requests

from flask import Flask, Response, request
from git import Repo
from datetime import datetime, timezone, timedelta

from sciit import IssueRepo
from sciit.cli.color import CPrint
from sciit.gitlab.pushhook import handle_push_event
from sciit.gitlab.issuehook import handle_issue_event

app = Flask(__name__)


class CONFIG:
    """An object containing all the necessary information about
    the configuration of the webservice.
    """
    repo = None
    api_token = None
    api_url = None
    project_id = None
    project_url = None
    path = None
    gitlab_cache = None
    last_push_hook = None
    last_issue_hook = None


def get_logger():
    """Initialises the logger for the webservice that allows for the logging
    of webservice events
    """
    global CONFIG
    logging.basicConfig(format='%(levelname)s:[%(asctime)s]cl %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        filename=CONFIG.path + '.log',
                        level=logging.INFO)


@app.route('/', methods=['POST'])
def index():
    """The single endpoint of the service handling all incoming
    webhooks accordingly.
    """
    global CONFIG

    data = request.get_json()

    #set configuration items
    CONFIG.api_token = os.environ['GITLAB_API_TOKEN']
    CONFIG.api_url = data['repository']['homepage'].rsplit(
        '/', 1)[0].rsplit('/', 1)[0] + '/api/v4/'
    CONFIG.project_id = data['project']['id']
    CONFIG.project_url = data['project']['web_url']
    CONFIG.path = data['project']['url'].rsplit('/', 1)[1]
    CONFIG.gitlab_cache = CONFIG.path + '.cache'
    event = request.headers.environ['HTTP_X_GITLAB_EVENT']
    get_logger()

    # download, build and set issue repo
    if CONFIG.repo is None or not os.path.exists(CONFIG.path):
        if os.path.exists(CONFIG.path):
            CONFIG.repo = IssueRepo(path=CONFIG.path)
        else:
            subprocess.run(['git', 'clone', '--mirror',
                            data['project']['url'], CONFIG.path], check=True)
            CONFIG.repo = IssueRepo(path=CONFIG.path)
            CONFIG.repo.build_issue_commits_from_all_commits()

    logging.info(f'received a {event} event')
    logging.info(f'using repository: {CONFIG.path}')

    if event == 'Push Hook':

        CONFIG.last_push_hook = datetime.now(timezone.utc)
        if CONFIG.last_issue_hook:
            delta = CONFIG.last_push_hook - CONFIG.last_issue_hook
            if delta < timedelta(seconds=10):
                return json.dumps({"status": "Rejected",
                                   "message": "This request originated from an Issue Hook"})
            else:
                return handle_push_event(CONFIG, data)
        else:
            return handle_push_event(CONFIG, data)

    elif event == 'Issue Hook':

        CONFIG.last_issue_hook = datetime.now(timezone.utc)
        if CONFIG.last_push_hook:
            delta = CONFIG.last_issue_hook - CONFIG.last_push_hook
            if delta < timedelta(seconds=10):
                return json.dumps({"status": "Rejected",
                                   "message": "This request originated from an Push Hook"})
            else:
                return handle_issue_event(CONFIG, data)
        else:
            return handle_issue_event(CONFIG, data)
    else:
        return Response({"status": "Failue", "message": f"Gitlab hook - {event} not supported"}, status=404)


@app.route('/status', methods=['GET'])
def status():
    """An endpoint to check the status of the webservice to determine its running state
    without making any changes
    """
    return json.dumps({"status": "running", "message": "The SCIIT-GitLab integration service is operational"})


@app.route('/init', methods=['POST'])
def init():
    """An endpoint that can be used to initialise the sciit repository
    """
    global CONFIG
    data = request.get_json()

    if CONFIG.repo is None or os.path.exists(CONFIG.path):
        import stat
        import shutil

        def onerror(func, path, excp_info):
            os.chmod(path, stat.S_IWUSR)
            func(path)
        shutil.rmtree(CONFIG.path, onerror=onerror)

    subprocess.run(['git', 'clone', '--mirror',
                    data['remote'], CONFIG.path], check=True)
    CONFIG.repo = IssueRepo(path=CONFIG.path)
    CONFIG.repo.build_issue_commits_from_all_commits()

    return json.dumps({"status": "Success", "message": f"{data['remote']} Issue Repository Initialized"})


def launch(args):
    """A helper function that launches the webservice from sciit
    cli
    """
    global CONFIG
    CONFIG.repo = args.repo
    if 'GITLAB_API_TOKEN' in os.environ:
        CONFIG.api_token = os.environ['GITLAB_API_TOKEN']
        app.run(host='0.0.0.0', port=5000)
    else:
        CPrint.bold_red(
            'Must specify gitlab api access token as environment variable')
        CPrint.bold('Set token to environment variable GITLAB_API_TOKEN')
        exit(127)


if __name__ == '__main__':
    args = type('args', (), {})
    args.repo = None
    launch(args)
