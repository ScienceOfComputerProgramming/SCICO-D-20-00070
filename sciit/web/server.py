# -*- coding: utf-8 -*-
"""Module that contains the functions needed to lauch the web
server.

:@author: Nystrom Edwards
:Created: 06 August 2018
"""
from flask import Flask, render_template
from sciit import IssueRepo
import markdown2

app = Flask(__name__)
history = None


@app.route("/")
def index():
    """The homepage of the web interface that shows all the open and
    closed issues stored in the tracker
    """
    data = {}
    data['Num Open Issues'] = len(
        [x for x in history.values() if x['status'] == 'Open'])
    data['Num Closed Issues'] = len(
        [x for x in history.values() if x['status'] == 'Closed'])
    return render_template('home.html', history=history, data=data)


@app.route("/<issue>")
def issue(issue):
    """The issue information page where all metadata an complexly
    inferred source control information is shown.
    """
    return render_template('issue.html', issue=history[issue])


def launch(args):
    """A helper function that builds issue tracker history and
    launches the webserver
    """
    global history
    history = args.repo.build_history()
    for item in history.values():
        if 'description' in item:
            item['description'] = markdown2.markdown(item['description'])
    app.run(debug=False)
