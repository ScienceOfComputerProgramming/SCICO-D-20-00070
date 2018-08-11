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

import requests
from flask import Flask, Response, jsonify, request
from git import Repo

from sciit import IssueRepo

app = Flask(__name__)
repo = None
path = 'remote.git'


def handle_push_event(data):
    """Handle push events make to the remote git repository

    """
    """
    @issue handle push events
    @description
    The webservice must be able to handle push events to the gitlab
    remote server such that if there are new issues in the codebase
    it will reach out to the gitlab api to create those new issues
    based on the commits received.

    Communicate with gitlab api to create and or update the issues
    based on what was pushed to the remote.
    @label feature
    """
    repo.git.execute(['git', 'fetch', '--all'])
    repo.sync()

    return '3200'


def handle_issue_events():
    """Handle issue events made in the gitlab issue tracker
    """
    """
    @issue handle issue events
    @description
    Handles the events where issues are created/updated/deleted from
    the gitlab issue tracker such that we are able to use the gitlab
    api to create commits and change files with our issue syntax.
    @label feature
    """


@app.route('/', methods=['POST'])
def index():
    """The single endpoint of the service handling all incoming 
    webhooks accordingly.
    """
    global repo
    event = request.headers.environ['HTTP_X_GITLAB_EVENT']
    data = request.get_json()

    # download and build repo
    if repo is None or not os.path.exists(path):
        if os.path.exists(path):
            repo = IssueRepo(path=path)
        else:
            subprocess.run(['git', 'clone', '--bare',
                            data['project']['url'], path], check=True)
            repo = IssueRepo(path=path)
            repo.cli = True
            repo.build()

    if event == 'Push Hook':
        return handle_push_event(data)
    else:
        return Response(status=500)


@app.route('/init', methods=['POST'])
def init():
    global repo
    data = request.get_json()

    if repo is None or os.path.exists(path):
        import stat
        import shutil

        def onerror(func, path, excp_info):
            os.chmod(path, stat.S_IWUSR)
            func(path)
        shutil.rmtree(path, onerror=onerror)

    subprocess.run(['git', 'clone', '--bare',
                    data['remote'], path], check=True)
    repo = IssueRepo(path=path)
    repo.cli = True
    repo.build()

    return jsonify({"message": f"{data['remote']} Issue Repository Initialized"})


def launch(args):
    """A helper function that launches the webservice from sciit
    cli
    """
    global repo
    repo = args.repo
    app.run(debug=True)


if __name__ == '__main__':
    app.run()
