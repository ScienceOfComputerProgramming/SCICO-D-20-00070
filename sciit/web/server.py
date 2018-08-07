
from flask import Flask, render_template
from sciit import IssueRepo
import markdown2

app = Flask(__name__)


@app.route("/")
def index():
    data = {}
    data['Num Open Issues'] = len(
        [x for x in history.values() if x['status'] == 'Open'])
    data['Num Closed Issues'] = len(
        [x for x in history.values() if x['status'] == 'Closed'])
    return render_template('home.html', history=history, data=data)


@app.route("/<issue>")
def issue(issue):
    return render_template('issue.html', issue=history[issue])


def launch(args):
    global history
    history = args.repo.build_history()
    for item in history.values():
        if 'description' in item:
            item['description'] = markdown2.markdown(item['description'])
    app.run(debug=True)
