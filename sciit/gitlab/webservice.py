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

from multiprocessing import Process

from flask import Flask, Response, request

from git import Repo

from sciit import IssueRepo
from sciit.cli.color import CPrint

app = Flask(__name__)
repo = None
api_token = None
path = 'remote.git'


def create_issue_note():
    """Creats a new issue note for gitlab issues
    """
    pass


def create_issue(issue_data):
    """Creates a new issue in gitlab
    """
    pass


def edit_issue(issue_data, old_data):
    """Edits an issue in gitlab
    """
    pass


def handle_push_event(data):
    """Handle push events make to the remote git repository

    Args:
        :(dict) data: data given in request webhook
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

    # get the new commits pushed to the repository
    if data['before'] == '0000000000000000000000000000000000000000':
        revision=data['after']
    else:
        revision=f'{data["before"]}..{data["after"]}'
    history=repo.build_history(revision)

    # get issues from gitlab
    api=data['repository']['homepage'].rsplit('/', 1)[0].rsplit('/', 1)[0]
    api += '/api/v4/'
    gitlab_issues=f'{api}projects/{data["project_id"]}/issues'
    gitlab_issues=requests.get(gitlab_issues, headers = {
                                 'Private-Token': api_token})
    gitlab_issues=json.loads(gitlab_issues.content)

    # checks if gitlab api token was successful
    if 'message' in gitlab_issues:
        if '404' in gitlab_issues['message']:
            return Response(json.dumps({"status": "Failure", "message": gitlab_issues['message']}), status = 404)

    issues_created=0
    issues_edited=0

    for issue in history.values():
        if gitlab_issues:
            if issue['id'] in [x['iid'] for x in gitlab_issues]:
                old_data=next(
                    (x for x in gitlab_issues if x['iid'] == issue['iid']))
                edit_issue(issue, old_data)
                issues_edited += 1
            else:
                create_issue(issue)
                issues_created += 1
        else:
            create_issue(issue)
            issues_created += 1
    return json.dumps({"status": "Success",
                       "issues_created": issues_created,
                       "issues_edited": issues_edited})


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


@app.route('/', methods = ['POST'])
def index():
    """The single endpoint of the service handling all incoming
    webhooks accordingly.
    """
    global repo
    global api_token
    api_token=os.environ['GITLAB_API_TOKEN']
    event=request.headers.environ['HTTP_X_GITLAB_EVENT']
    data=request.get_json()

    # download and build repo
    if repo is None or not os.path.exists(path):
        if os.path.exists(path):
            repo=IssueRepo(path = path)
        else:
            subprocess.run(['git', 'clone', '--bare',
                            data['project']['url'], path], check = True)
            repo=IssueRepo(path = path)
            repo.cli=True
            repo.build()

    if event == 'Push Hook':
        return handle_push_event(data)
    else:
        return Response({"status": "Failue", "message": f"Gitlab hook - {event} not supported"}, status = 404)


@app.route('/init', methods = ['POST'])
def init():
    global repo
    data=request.get_json()

    if repo is None or os.path.exists(path):
        import stat
        import shutil

        def onerror(func, path, excp_info):
            os.chmod(path, stat.S_IWUSR)
            func(path)
        shutil.rmtree(path, onerror = onerror)

    subprocess.run(['git', 'clone', '--bare',
                    data['remote'], path], check = True)
    repo=IssueRepo(path = path)
    repo.cli=True
    repo.build()

    return json.dumps({"status": "Success", "message": f"{data['remote']} Issue Repository Initialized"})


def launch(args):
    """A helper function that launches the webservice from sciit
    cli
    """
    global repo
    global api_token
    repo=args.repo
    if 'GITLAB_API_TOKEN' in os.environ:
        api_token=os.environ['GITLAB_API_TOKEN']
        app.run(debug = True)
    else:
        CPrint.bold_red('Must specify gitlab api access token')
        CPrint.bold('Copy token to a file named \'token\' in webserver root')
        exit(127)


if __name__ == '__main__':
    args=type('args', (), {})
    args.repo=None
    launch(args)
