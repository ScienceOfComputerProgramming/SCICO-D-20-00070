# -*- coding: utf-8 -*-
"""Module that contains the functions needed to lauch the gitlab
webservice. Note that this webservice cannot run together with
the local git sciit web interface

:@author: Nystrom Edwards
:Created: 07 August 2018
"""
import logging
import requests
from flask import Flask

app = Flask(__name__)
repo = None


def handle_push_event():
    """Handle push events make to the remote git repository

    """
    """
    @issue handle push events
    @description
    The webservice must be able to handle push events to the gitlab
    remote server such that if there are new issues in the codebase
    it will reach out to the gitlab api to create those new issues
    based on the commits received
    @label feature
    """


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


@app.route("/")
def index():
    """The single endpoint of the service handling all incoming 
    webhooks accordingly.
    """
    return str(repo.build_history())


def launch(args):
    """A helper function that launches the webservice from sciit
    cli
    """
    global repo
    repo = args.repo
    app.run(debug=True)


if __name__ == '__main__':
    launch(None)
