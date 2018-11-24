# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

import hashlib
import markdown2
import re
from datetime import datetime

from git import Commit
from gitdb.util import hex_to_bin

__all__ = ('IssueSnapshot', 'Issue')

time_format = '%a %b %d %H:%M:%S %Y %z'

def record_revision(commit, changes=None):

    date_string = commit.authored_datetime.strftime(time_format)

    result = {
        'commitsha': commit.hexsha,
        'date': date_string,
        'author': commit.author.name,
        'summary': commit.summary
        }
    if changes is not None:
        result['changes'] = changes
    return result


class IssueSnapshot(object):
    __slots__ = ('commit', 'data', 'title', 'description', 'assignees', 'due_date', 'label', 'weight', 'priority',
                 'title','filepath', 'issue_id', 'blockers', 'in_branches')

    _children = dict()

    def __init__(self, commit, data, in_branches):

        self.commit = commit
        self.data = data
        self.in_branches = in_branches

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
        return str(self.issue_id) + '@' + str(self.commit.hexsha) +  ' in ' + str(self.in_branches)

    def __repr__(self):
        return self.__str__()

    def _find_child_shas(self):
        rev_list = self.commit.repo.git.execute(['git', 'rev-list', '--all', '--children'])
        pattern = re.compile(r'(?:' + self.commit.hexsha + ')(.*)')

        matched_strings = pattern.findall(rev_list)
        if len(matched_strings) > 0:
            return matched_strings[0].strip(' ').split(' ')
        else:
            return list()

    @property
    def children(self):
        if self.commit.hexsha not in IssueSnapshot._children:

            children = list()

            child_shas = self._find_child_shas()

            if len(child_shas) > 0 and child_shas[0] != '':
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
        return self.commit.authored_datetime.strftime(time_format)


class Issue(object):

    def __init__(self, issue_id, all_issues, head_commits):

        self.issue_id = issue_id
        self.all_issues = all_issues
        self.head_commits = head_commits

        self.issue_snapshots = list()

        self._open_in_branches = None

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
        """
        Issue status life cycle based on a github workflow.

        open in feature (Proposed)
        open in feature, master and master branch is equal to or ahead of feature branch (Accepted)
        closed in feature and not in master (Rejected).
        open in feature, master and feature is ahead of accepting commit in master (In Progress)
        closed in feature, open in master (In Review)
        closed in feature, closed in master (Closed)
        """
        feature_branch = self.issue_id

        in_branches = self.in_branches
        open_in_branches = self.open_in_branches
        closed_in_branches = self.closed_in_branches
        accepted_date = self.accepted_date
        latest_date_in_feature_branch = self.latest_date_in_feature_branch

        if open_in_branches == {feature_branch}:
            return 'Open', 'Proposed'

        elif 'master' in open_in_branches:
            if None not in {accepted_date, latest_date_in_feature_branch} and \
                    accepted_date < latest_date_in_feature_branch:
                return 'Open', 'In Progress'
            elif feature_branch in closed_in_branches:
                return 'Open', 'In Review'
            else:
                return 'Open', 'Accepted'

        elif feature_branch in closed_in_branches and 'master' not in in_branches:
            return 'Closed', 'Rejected'
        elif 'master' in closed_in_branches:
            return 'Closed', 'Resolved'
        elif open_in_branches == set():
            return 'Closed', 'Unknown'
        else:
            return 'Open', 'Unknown'

    @property
    def closing_commit(self):

        def _child_of_last_commit_in_branch(branch_name):
            for issue_snapshot in reversed(self.issue_snapshots):
                if branch_name in issue_snapshot.in_branches:
                    if len(issue_snapshot.children) > 0:
                        return issue_snapshot.children[0]
                    else:
                        break
            return None

        status, sub_status = self.status
        if not status == 'Closed':
            return None

        if sub_status == 'Resolved':
            return _child_of_last_commit_in_branch('master')
        elif sub_status == 'Rejected':
            return _child_of_last_commit_in_branch(self.issue_id)
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
    def accepting_commit_in_master(self):
        """
        :return: The first commit in the master branch in which the issue appears.
        """
        for issue_snapshot in self.issue_snapshots:
            if 'master' in issue_snapshot.in_branches:
                return issue_snapshot.commit
        return None

    @property
    def accepted_date(self):
        if self.accepting_commit_in_master is not None:
            return self.accepting_commit_in_master.authored_datetime
        else:
            return None

    @property
    def latest_commit_in_feature_branch(self):
        for issue_snapshot in reversed(self.issue_snapshots):
            if self.issue_id in issue_snapshot.in_branches:
                return issue_snapshot.commit
        return None

    @property
    def latest_date_in_feature_branch(self):
        if self.latest_commit_in_feature_branch is not None:
            return self.latest_commit_in_feature_branch.authored_datetime
        else:
            return None

    @property
    def activity(self):
        result = list()

        for issue_snapshot in self.issue_snapshots:
            result.append(record_revision(issue_snapshot.commit))

        if self.status[0] == 'Closed' and self.closing_commit is not None:
            result.append(record_revision(self.closing_commit))

        return result

    @property
    def revisions(self):

        result = list()

        if self.status[0] == 'Closed' and self.closing_commit is not None:
            result.append(record_revision(self.closing_commit, {'status': 'Closed'}))

        for older, newer in zip(self.issue_snapshots[:-1], self.issue_snapshots[1:]):
            changes = dict()
            for k, v in older.data.items():
                if k not in newer.data or newer.data[k] != v:
                    changes[k] = v

            if 'hexsha' in changes:
                del changes['hexsha']

            if len(changes) > 0:
                result.append(record_revision(newer.commit, changes))

        original_values = self.oldest_issue_snapshot.data
        if 'hexsha' in original_values:
            del original_values['hexsha']

        result.append(record_revision(self.oldest_issue_snapshot.commit, original_values))

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
    def open_in_branches(self):
        if not self._open_in_branches:
            issue_snapshot_commit_hexshas = [issue_snapshot.commit.hexsha for issue_snapshot in self.issue_snapshots]
            self._open_in_branches = set()
            for name, hexsha in self.head_commits.items():
                if hexsha in issue_snapshot_commit_hexshas:
                    self._open_in_branches.add(name)
        return self._open_in_branches

    @property
    def closed_in_branches(self):
        return self.in_branches - self.open_in_branches

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
        return self.issue_id + " " + self.status[0]

    def __repr__(self):
        return "Issue " + self.issue_id + " (" + self.status[0] + ") as of " + self.newest_issue_snapshot.commit.hexsha

    def update(self, issue_snapshot):
        """
        Update the content of the issue history, based on newly discovered, *older* information.
        """
        self.issue_snapshots.append(issue_snapshot)
        self.issue_snapshots.sort(
            key=lambda issue_snapshot: datetime.strptime(issue_snapshot.date_string, time_format))

