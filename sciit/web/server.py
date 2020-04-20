# -*- coding: utf-8 -*-

"""
Entry point for the web service view of a Sciit issue tracker.
"""

from flask import Flask, render_template
from git import Repo

from sciit import IssueRepo


app = Flask(__name__)


global_issue_repository = None


@app.route("/")
def index():
    """
    The homepage of the web interface that shows all the open and closed issues stored in the tracker.
    """
    history = global_issue_repository.build_history()
    data = dict()

    data['Num Open Issues'] = sum(map(lambda issue: 1 if issue.status[0] == 'Open' else 0, history.values()))
    data['Num Closed Issues'] = sum(map(lambda issue: 1 if issue.status[0] == 'Closed' else 0, history.values()))

    return render_template('home.html', history=history, data=data)


@app.route("/<issue_id>")
def issue(issue_id):
    """
    Page for showing the content and history of an issue, derived from its repository commits.
    """
    history = global_issue_repository.build_history()
    return render_template('issue.html', issue=history[issue_id])


def launch(issue_repository=None):

    global global_issue_repository

    if issue_repository is None:
        git_repository = Repo(search_parent_directories=True)
        global_issue_repository = IssueRepo(git_repository)
    else:
        global_issue_repository = issue_repository

    app.run(debug=False)

