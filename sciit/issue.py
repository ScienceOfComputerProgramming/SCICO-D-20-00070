# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

import hashlib
import markdown2
import re

from git import Commit
from gitdb.util import hex_to_bin

__all__ = ('IssueSnapshot', 'Issue')


class IssueSnapshot(object):
    __slots__ = ('commit', 'data', 'title', 'description', 'assignees', 'due_date', 'label', 'weight', 'priority',
                 'title','filepath', 'issue_id', 'blockers')

    _in_branches = dict()
    _children = dict()

    def __init__(self, commit, data):

        self.commit = commit
        self.data = data

        if 'issue_id' in self.data:
            self.issue_id = self.data['issue_id']
        if 'title' in self.data:
            self.title = self.data['title']
        if 'description' in self.data:
            self.description = self.data['description']
        if 'assignees' in self.data:
            self.assignees = self.data['assignees']
        if 'due_date' in self.data:
            self.due_date = self.data['due_date']
        if 'label' in self.data:
            self.label = self.data['label']
        if 'weight' in self.data:
            self.weight = self.data['weight']
        if 'priority' in self.data:
            self.priority = self.data['priority']
        if 'filepath' in self.data:
            self.filepath = self.data['filepath']
        if 'blockers' in self.data:
            self.blockers = self.data['blockers']

    def __lt__(self, other):
        return self.issue_id < other.issue_id

    def __eq__(self, other):
        return self.issue_id == other.issue_id

    def __gt__(self, other):
        return self.issue_id > other.issue_id

    def __hash__(self):
        sha = hashlib.sha1(self.issue_id.encode())
        sha = sha.hexdigest()
        return int(sha, 16)

    def __str__(self):
        return 'Issue#' + str(self.issue_id) + ' in commit ' + str(self.commit.hexsha)

    @property
    def children(self):
        if self.commit.hexsha not in IssueSnapshot._children:

            children = list()

            rev_list = self.commit.repo.git.execute(['git', 'rev-list', '--all', '--children'])

            pattern = re.compile(r'(?:' + self.commit.hexsha + ')(.*)')
            child_shas = pattern.findall(rev_list)[0]
            child_shas = child_shas.strip(' ').split(' ')
            if child_shas[0] != '':
                for child in child_shas:
                    children.append(Commit(self.commit.repo, hex_to_bin(child)))

            IssueSnapshot._children[self.commit.hexsha] = children

        return IssueSnapshot._children[self.commit.hexsha]

    @property
    def size(self):
        return len(str(self.data))

    @property
    def author_name(self):
        return self.commit.author.name

    @property
    def date_string(self):
        time_format = '%a %b %d %H:%M:%S %Y %z'
        return self.commit.authored_datetime.strftime(time_format)

    @property
    def in_branches(self):
        if self.commit.hexsha not in IssueSnapshot._in_branches:
            IssueSnapshot._in_branches[self.commit.hexsha] = \
                self.commit.repo.git.execute(['git', 'branch', '--contains', self.commit.hexsha])\
                .replace('*', '') \
                .replace(' ', '').split('\n')
        return IssueSnapshot._in_branches[self.commit.hexsha]


class Issue(object):

    def __init__(self, issue_id, all_issues):

        self.issue_id = issue_id

        self.all_issues = all_issues

        self.issue_snapshots = list()

        self.open_in = set()

    @property
    def newest_issue_snapshot(self):
        return self.issue_snapshots[-1]

    @property
    def oldest_issue_snapshot(self):
        return self.issue_snapshots[0]

    @property
    def last_author(self):
        return self.newest_issue_snapshot.commit.author.name

    @property
    def creator(self):
        return self.oldest_issue_snapshot.commit.author.name

    @property
    def created_date(self):
        return self.oldest_issue_snapshot.date_string

    @property
    def last_authored_date(self):
        return self.newest_issue_snapshot.date_string

    def newest_value_of_issue_property(self, p):
        for issue_snapshot in reversed(self.issue_snapshots):
            if hasattr(issue_snapshot, p):
                return getattr(issue_snapshot, p)
        return None

    @property
    def title(self):
        return self.newest_value_of_issue_property('title')

    @property
    def description(self):
        return self.newest_value_of_issue_property('description')

    @property
    def description_as_html(self):
        return markdown2.markdown(self.description) if self.description else None

    @property
    def assignees(self):
        return self.newest_value_of_issue_property('assignees')

    @property
    def due_date(self):
        return self.newest_value_of_issue_property('due_date')

    @property
    def label(self):
        return self.newest_value_of_issue_property('label')

    @property
    def weight(self):
        return self.newest_value_of_issue_property('weight')

    @property
    def priority(self):
        return self.newest_value_of_issue_property('priority')

    @property
    def file_paths(self):
        result = dict()
        for issue_snapshot in self.issue_snapshots:
            for branch in issue_snapshot.in_branches:
                if branch not in result:
                    result[branch] = issue_snapshot.data['filepath']
        return result

    @property
    def file_path(self):
        return self.newest_issue_snapshot.data['filepath']

    @property
    def participants(self):
        result = set()
        for issue_snapshot in self.issue_snapshots:
            result.add(issue_snapshot.author_name)
        return result

    @property
    def status(self):
        return 'Open' if len(self.open_in) > 0 else 'Closed'

    @property
    def closing_commit(self):
        if self.status == 'Closed':
            return self.newest_issue_snapshot.children[0]
        else:
            return None

    @property
    def closer(self):
        return self.closing_commit.author.name if self.closing_commit else None

    @property
    def closed_date(self):
        time_format = '%a %b %d %H:%M:%S %Y %z'
        return self.closing_commit.authored_datetime.strftime(time_format) if self.closing_commit else None

    @property
    def closing_summary(self):
        return self.closing_commit.summary if self.closing_commit else None

    @property
    def activity(self):
        result = list()
        for issue_snapshot in self.issue_snapshots:
            result.append(
                {
                    'commitsha': issue_snapshot.commit.hexsha,
                    'date': issue_snapshot.date_string,
                    'author': issue_snapshot.author_name,
                    'summary': issue_snapshot.commit.summary})

        if self.status == 'Closed':

            closing_activity = \
                {
                    'commitsha': self.closing_commit.hexsha,
                    'date': self.closed_date,
                    'author': self.closer,
                    'summary': self.closing_summary + ' (closed)'
                }
            result.insert(0, closing_activity)

        return result

    @property
    def revisions(self):

        result = list()

        def record_revision(commit, changes):

            time_format = '%a %b %d %H:%M:%S %Y %z'
            change_date = commit.authored_datetime.strftime(time_format)

            result.append(
                {
                    'issuesha': commit.hexsha,
                    'date': change_date,
                    'author': commit.author.name,
                    'changes': changes,
                    'message': commit.summary
                }
            )

        if self.status == 'Closed':
            record_revision(self.closing_commit, {'status': 'Closed'})

        for older, newer in zip(self.issue_snapshots[:-1], self.issue_snapshots[1:]):
            changes = dict()
            for k, v in older.data.items():
                if k not in newer.data or newer.data[k] != v:
                    changes[k] = v

            if 'hexsha' in changes:
                del changes['hexsha']

            if len(changes) > 0:
                record_revision(newer.commit, changes)

        original_values = self.oldest_issue_snapshot.data
        if 'hexsha' in original_values:
            del original_values['hexsha']

        record_revision(self.oldest_issue_snapshot.commit, original_values)

        return result

    @property
    def size(self):
        return sum([issue_snapshot.size for issue_snapshot in self.issue_snapshots])

    @property
    def in_branches(self):
        result = set()
        for issue_snapshot in self.issue_snapshots:
            result.update(issue_snapshot.in_branches)
        return result

    @property
    def blockers(self):

        result = dict()

        latest_blockers_str = self.newest_value_of_issue_property('blockers')

        if latest_blockers_str is not None:
            blocker_issue_ids = [s.strip() for s in latest_blockers_str.split(',')]

            for blocker_issue_id in blocker_issue_ids:
                result[blocker_issue_id] = self.all_issues.get(blocker_issue_id, None)

        return result

    def __str__(self):
        return self.issue_id + " " + self.status

    def __repr__(self):
        return "Issue " + self.issue_id + " (" + self.status + ") as of " + self.newest_issue_snapshot.commit.hexsha


    def update(self, issue_snapshot):
        """
        Update the content of the issue history, based on newly discovered, *older* information.
        """
        self.issue_snapshots.append(issue_snapshot)

