import json
from datetime import datetime, timezone, timedelta

import dateutil.parser as dateparser
from threading import Thread
from sciit.gitlab.commitapi import create_commit


def handle_issue_event(CONFIG, data):
    """Handle issue events made in the gitlab issue tracker
    """
    def worker(CONFIG, data):
        if data['object_attributes']['last_edited_at'] is not None:
            edited = dateparser.parse(
                data['object_attributes']['last_edited_at'])
            now = datetime.now(timezone.utc)
            delta = now - edited

            # check if the hook was triggered by gitlab interface and not
            # the api requests made in the push hooks
            if delta < timedelta(seconds=5):
                CONFIG.repo.git.execute(['git', 'fetch', '--all'])
                CONFIG.repo.sync()

                issue = {}
                issue['iid'] = data['object_attributes']['iid']
                issue['title'] = data['object_attributes']['title']
                issue['description'] = data['object_attributes']['description']
                commit = {}
                commit['author_name'] = data['user']['username']
                create_commit(CONFIG, issue, commit)

    t = Thread(target=worker, args=(CONFIG, data))
    t.start()

    return json.dumps({"status": "Success",
                       "message": "Your issues were commited to gitlab"})
