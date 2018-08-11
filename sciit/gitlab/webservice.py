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
import hashlib

from multiprocessing import Process, Manager

from flask import Flask, Response, request

from git import Repo

from sciit import IssueRepo
from sciit.cli.color import CPrint

app = Flask(__name__)
repo = None
api_token = None
api_url = None
project_id = None
path = 'remote.git'
gitlab_cache = 'gitlab'


def create_issue_note():
    """Creats a new issue note for gitlab issues
    """
    pass


def create_issue(issue_data, multi_list):
    """Creates a new issue in gitlab
    """
    issue = {}
    issue['id'] = project_id
    issue['title'] = issue_data['title']
    if 'description' in issue_data:
        issue['description'] = issue_data['description']
    if 'label' in issue_data:
        issue['labels'] = issue_data['label']
    if 'due_date' in issue_data:
        issue['due_date'] = issue_data['due_date']
    if 'weight' in issue_data:
        issue['weight'] = issue_data['weight']
    # issue['created_at'] = issue_data['created_date']

    r = requests.post(f'{api_url}/projects/{project_id}/issues',
                      headers={'Private-Token': api_token},
                      json=issue)
    if r.status_code == 201:
        iid = json.loads(r.content)['iid']
        multi_list.append((issue_data['id'], iid))
    return r.status_code


def edit_issue(issue_data, pair):
    """Edits an issue in gitlab
    """
    # get issues from gitlab
    gitlab_issues = f'{api_url}projects/{project_id}/issues'
    gitlab_issues = requests.get(gitlab_issues, headers={
        'Private-Token': api_token})
    gitlab_issues = json.loads(gitlab_issues.content)

    # checks if gitlab api token was successful
    if 'message' in gitlab_issues:
        if '404' in gitlab_issues['message']:
            return Response(json.dumps({"status": "Failure", "message": gitlab_issues['message']}), status=404)
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
        revision = data['after']
    else:
        revision = f'{data["before"]}..{data["after"]}'
    history = repo.build_history(revision)

    issues_created = 0
    issues_edited = 0
    issues_total = 0

    # get last set of cached issues initially none
    if os.path.exists(gitlab_cache):
        with open(gitlab_cache, 'r') as issue_cache:
            cache = json.loads(issue_cache.read())
    else:
        cache = None

    # a manager for the list of issue cache
    man = Manager()
    multi_list = man.list([])
    procs = []

    for issue in history.values():
        if cache:
            pair = [x for x in cache if x[0] == issue['id']]
            if pair:
                issues_edited += 1
                edit_issue(issue, pair[0])
                # procs.append(
                #     Process(target=edit_issue, args=(issue, old_data)))
                # procs[issues_total].start()
            else:
                issues_created += 1
                create_issue(issue, man)
                # procs.append(Process(target=create_issue,
                #                      args=(issue, multi_list)))
                # procs[issues_total].start()
        else:
            issues_created += 1
            create_issue(issue, man)
            # procs.append(Process(target=create_issue,
            #                      args=(issue, multi_list)))
            # procs[issues_total].start()
        issues_total += 1

    # wait for processes to finish
    # for i in range(issues_total):
    #     procs[i].join()

    # write the changes to the cache
    if cache:
        cache.append([x for x in multi_list])
    else:
        cache = [x for x in multi_list]
    with open(gitlab_cache, 'w') as issue_cache:
        issue_cache.write(json.dumps(cache))

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


@app.route('/', methods=['POST'])
def index():
    """The single endpoint of the service handling all incoming
    webhooks accordingly.
    """
    global repo
    global api_token
    global api_url
    global project_id

    data = request.get_json()
    api_token = os.environ['GITLAB_API_TOKEN']
    api_url = data['repository']['homepage'].rsplit(
        '/', 1)[0].rsplit('/', 1)[0] + '/api/v4/'
    project_id = data['project_id']
    event = request.headers.environ['HTTP_X_GITLAB_EVENT']

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
        return Response({"status": "Failue", "message": f"Gitlab hook - {event} not supported"}, status=404)


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

    return json.dumps({"status": "Success", "message": f"{data['remote']} Issue Repository Initialized"})


def launch(args):
    """A helper function that launches the webservice from sciit
    cli
    """
    global repo
    global api_token
    repo = args.repo
    if 'GITLAB_API_TOKEN' in os.environ:
        api_token = os.environ['GITLAB_API_TOKEN']
        app.run(debug=True)
    else:
        CPrint.bold_red('Must specify gitlab api access token')
        CPrint.bold('Copy token to a file named \'token\' in webserver root')
        exit(127)


if __name__ == '__main__':
    args = type('args', (), {})
    args.repo = None
    launch(args)
