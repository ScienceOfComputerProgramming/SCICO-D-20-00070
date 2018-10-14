# -*- coding: utf-8 -*-
"""
Functions needed to launch the web server.
"""

from flask import Flask, render_template
from git import Repo

from sciit import IssueRepo

app = Flask(__name__)
history = None


@app.route("/")
def index():
    """
    The homepage of the web interface that shows all the open and closed issues stored in the tracker.
    """
    data = dict()
    data['Num Open Issues'] = len([x for x in history.values() if x.status == 'Open'])
    data['Num Closed Issues'] = len([x for x in history.values() if x.status == 'Closed'])
    return render_template('home.html', history=history, data=data)


@app.route("/<issue_id>")
def issue(issue_id):
    """
    The page for showing the content and history of an issue, derived from it's repository commits.
    """
    return render_template('issue.html', issue=history[issue_id])


def launch(issue_repository=None):

    if issue_repository is None:
        git_repository = Repo(search_parent_directories=True)
        repo = IssueRepo(git_repository)

    """
    Builds issue tracker history and launches the webserver
    """
    global history
    history = issue_repository.build_history()
    app.run(debug=False)

