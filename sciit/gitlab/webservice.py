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
