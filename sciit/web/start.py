
from flask import Flask, render_template
from sciit import IssueRepo

repo = IssueRepo()
history = repo.build_history()
app = Flask(__name__)


@app.route("/")
def index():
    return render_template('base.html', title='SCIIT')


if __name__ == '__main__':
    app.run()
