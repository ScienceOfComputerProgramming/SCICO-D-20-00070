import json
from datetime import datetime, timezone, timedelta

import dateutil.parser as dateparser
from sciit.gitlab.commitapi import create_commit


def handle_issue_event(CONFIG, data):
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
    if data['object_attributes']['last_edited_at'] is not None:
        edited = dateparser.parse(data['object_attributes']['last_edited_at'])
        now = datetime.now(timezone.utc)
        delta = now - edited

        # check if the hook was triggered by gitlab interface and not
        # the api requests made in the push hooks
        if delta > timedelta(seconds=5):
            CONFIG.repo.git.execute(['git', 'fetch', '--all'])
            CONFIG.repo.sync()

            issue = {}
            issue['iid'] = data['object_attributes']['iid']
            issue['title'] = data['object_attributes']['title']
            issue['description'] = data['object_attributes']['description']
            commit = {}
            commit['author_name'] = data['user']['username']
            create_commit(CONFIG, issue, commit)
        else:
            return json.dumps({"status": "Invalid",
                               "messsage": "Skipped: this conflicts with Push Hook"})

    return json.dumps({"status": "Success",
                       "message": "Your issues were commited to gitlab"})
