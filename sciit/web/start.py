
from flask import Flask, render_template
from sciit import IssueRepo

app = Flask(__name__)


@app.route("/")
def index():
    return render_template('home.html', history=history)


def startweb(args):
    global history
    history = args.repo.build_history()
    app.run(debug=True)
