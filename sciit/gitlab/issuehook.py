import json
import logging
from datetime import datetime, timezone, timedelta

import dateutil.parser as dateparser
from threading import Thread
from sciit.gitlab.commitapi import create_commit


def handle_issue_event(CONFIG, data):
    """Handle issue events made in the gitlab issue tracker
    """

    if data['object_attributes']['last_edited_at'] is not None:
        edited = dateparser.parse(
            data['object_attributes']['last_edited_at'])
        now = datetime.now(timezone.utc)
        delta = now - edited
    else:
        edited = dateparser.parse(
            data['object_attributes']['created_at'])
        now = datetime.now(timezone.utc)
        delta = now - edited

    logging.debug(f'seconds past = {delta.seconds}')
    if delta > timedelta(seconds=2):
        return json.dumps({"status": "Rejected",
                           "message": "This request must not be handled"})

    def worker(CONFIG, data):
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
    logging.info('worker thread launched')

    return json.dumps({"status": "Success",
                       "message": "Your issues were commited to gitlab"})
