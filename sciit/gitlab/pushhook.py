import json
import os
import logging
from multiprocessing import Manager
from threading import Thread

from sciit.gitlab.issueapi import create_issue, edit_issue


def handle_push_event(CONFIG, data):
    """Handle push events make to the remote git repository
    """

    CONFIG.repo.git.execute(['git', 'fetch', '--all'])
    CONFIG.repo.sync()

    # get the new commits pushed to the repository
    if data['before'] == '0000000000000000000000000000000000000000':
        revision = data['after']
    else:
        revision = f'{data["before"]}..{data["after"]}'
    history = CONFIG.repo.build_history(revision)
    logging.info(f'revision history used {revision}')

    # get last set of cached issues initially none
    if os.path.exists(CONFIG.gitlab_cache):
        with open(CONFIG.gitlab_cache, 'r') as issue_cache:
            cache = json.loads(issue_cache.read())
            logging.debug('Cache exists')
    else:
        cache = None
        logging.debug('No cache exists')

    # a manager for the list of issue cache
    man = Manager()
    multi_list = man.list([])
    procs = []
    issues_total = 0

    for issue in history.values():
        if cache:
            pair = [x for x in cache if x[0] == issue['id']]
            if pair:
                procs.append(
                    Thread(target=edit_issue, args=(CONFIG, issue, pair[0])))
                procs[issues_total].start()
            else:
                procs.append(Thread(target=create_issue,
                                    args=(CONFIG, issue, multi_list)))
                procs[issues_total].start()
        else:
            procs.append(Thread(target=create_issue,
                                args=(CONFIG, issue, multi_list)))
            procs[issues_total].start()
        issues_total += 1

    # wait for subprocesses to finish
    for i in range(issues_total):
        procs[i].join()

    # write the changes to the cache
    multi_list = [x for x in multi_list]
    if cache:
        if multi_list:
            cache.extend(multi_list)
    else:
        cache = multi_list
    with open(CONFIG.gitlab_cache, 'w') as issue_cache:
        issue_cache.write(json.dumps(cache))
        logging.info('Writing issues to cache')

    return json.dumps({"status": "Success",
                       "message": "Your issues were updated"})
