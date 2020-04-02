# -*- coding: utf-8 -*-

import hashlib
import os
import re

import markdown2

from git import Commit
from gitdb.util import hex_to_bin


__all__ = ('IssueSnapshot', 'Issue')


TIME_FORMAT = '%a %b %d %H:%M:%S %Y %z'


def _make_revision_dictionary(commit, changes=None):

    date_string = commit.authored_datetime.strftime(TIME_FORMAT)

    result = {
        'hexsha': commit.hexsha,
        'date': date_string,
        'author': commit.author.name,
        'summary': commit.summary
        }

    if changes is not None:
        result['changes'] = changes

    return result


class IssueSnapshot:

    __slots__ = ('commit', 'data', 'in_branches',
                 'title', 'description', 'assignees', 'due_date', 'labels', 'weight', 'priority', 'title', 'file_path',
                 'start_position', 'end_position', 'issue_id', 'blockers')

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
        if 'labels' in self.data:
            self.labels = self.data['labels']
        if 'weight' in self.data:
            self.weight = self.data['weight']
        if 'priority' in self.data:
            self.priority = self.data['priority']

        if 'file_path' in self.data:
            self.file_path = self.data['file_path']
        if 'start_position' in self.data:
            self.start_position = self.data['start_position']
        if 'end_position' in self.data:
            self.end_position = self.data['end_position']

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
        return f'{str(self.issue_id)}@{str(self.commit.hexsha)} in {str(self.in_branches)}'

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
    def child_commits(self):
        if self.commit.hexsha not in IssueSnapshot._children:

            children = list()

            child_shas = self._find_child_shas()

            if len(child_shas) > 0 and child_shas[0] != '':
                for child in child_shas:
                    children.append(Commit(self.commit.repo, hex_to_bin(child)))

            IssueSnapshot._children[self.commit.hexsha] = children

        return IssueSnapshot._children[self.commit.hexsha]

    @property
    def author_name(self):
        return self.commit.author.name

    @property
    def date_string(self):
        return self.commit.authored_datetime.strftime(TIME_FORMAT)

    @property
    def date(self):
        return self.commit.authored_datetime


class Issue:

    def __init__(self, issue_id, all_issues, head_commits):

        self.issue_id = issue_id
        self.all_issues = all_issues
        self.head_commits = head_commits

        self.issue_snapshots = list()

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
        return self.oldest_issue_snapshot.date

    @property
    def created_date_string(self):
        return self.oldest_issue_snapshot.date_string

    @property
    def last_authored_date(self):
        return self.newest_issue_snapshot.date

    @property
    def last_authored_date_string(self):
        return self.newest_issue_snapshot.date_string

    def newest_value_of_issue_property(self, issue_property):
        for issue_snapshot in reversed(self.issue_snapshots):
            if hasattr(issue_snapshot, issue_property):
                return getattr(issue_snapshot, issue_property)
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
    def labels(self):
        labels_str = self.newest_value_of_issue_property('labels')
        if labels_str is None:
            return []
        else:
            return [label.strip() for label in labels_str.split(',')]

    @property
    def weight(self):
        return self.newest_value_of_issue_property('weight')

    @property
    def priority(self):
        return self.newest_value_of_issue_property('priority')

    @property
    def start_position(self):
        return self.newest_value_of_issue_property('start_position')

    @property
    def end_position(self):
        return self.newest_value_of_issue_property('end_position')

    @property
    def file_paths(self):
        result = dict()
        for issue_snapshot in self.issue_snapshots:
            for branch in issue_snapshot.in_branches:
                if branch not in result:
                    result[branch] = issue_snapshot.data['file_path']
        return result

    @property
    def file_path(self):
        return self.newest_issue_snapshot.data['file_path']

    @property
    def working_file_path(self):
        return self.newest_issue_snapshot.commit.repo.working_dir + os.sep + self.file_path

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

        if feature_branch in open_in_branches and 'master' not in in_branches:
            return 'Open', 'Proposed'

        elif 'master' in open_in_branches:
            if feature_branch in open_in_branches and \
                    None not in {accepted_date, latest_date_in_feature_branch} and \
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
            return 'Open', 'Non-Feature'

    @property
    def duration(self):
        if self.in_progress_commit is None or self.closing_commit is None:
            return None
        else:
            return self.closing_commit.authored_datetime - self.in_progress_commit.authored_datetime

    @property
    def in_progress_commit(self):
        return self.issue_snapshots[0].child_commits[0] if len(self.issue_snapshots[0].child_commits) > 0 else None

    @property
    def work_begun_date(self):
        return self.in_progress_commit.authored_datetime.strftime(TIME_FORMAT) if self.in_progress_commit else None

    @property
    def initiator(self):
        return self.in_progress_commit.author.name if self.in_progress_commit else None

    @property
    def closing_commit(self):

        def _child_of_last_commit_in_branch(branch_name):
            for issue_snapshot in reversed(self.issue_snapshots):
                if branch_name in issue_snapshot.in_branches:
                    if len(issue_snapshot.child_commits) > 0:
                        return issue_snapshot.child_commits[0]
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
        return self.closing_commit.authored_datetime.strftime(TIME_FORMAT) if self.closing_commit else None

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

    def _get_snapshot_for_commit_hexsha(self, commit_hexsha):
        for issue_snapshot in self.issue_snapshots:
            if issue_snapshot.commit.hexsha == commit_hexsha:
                return issue_snapshot
        return None

    def changed_by_commit(self, commit_hexsha):

        if self.closing_commit is not None and self.closing_commit.hexsha == commit_hexsha:
            return True

        commit_issue_snapshot = self._get_snapshot_for_commit_hexsha(commit_hexsha)

        if commit_issue_snapshot is None:
            return False

        parent_commits = commit_issue_snapshot.commit.parents

        if len(parent_commits) == 0:
            return True

        parent_issue_snapshots = \
            {issue_snapshot for issue_snapshot in self.issue_snapshots if issue_snapshot.commit in parent_commits}

        if len(parent_issue_snapshots) != len(parent_commits):
            return True

        def remove_start_and_end_position(data):
            irrelevant_keys = {'start_position', 'end_position'}
            return {key: value for key, value in data.items() if key not in irrelevant_keys}

        latest_data = remove_start_and_end_position(commit_issue_snapshot.data)

        for parent_issue_snapshot in parent_issue_snapshots:
            parent_data = remove_start_and_end_position(parent_issue_snapshot.data)
            if parent_data != latest_data:
                return True

        return False

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
            result.append(_make_revision_dictionary(issue_snapshot.commit))

        if self.status[0] == 'Closed' and self.closing_commit is not None:
            result.append(_make_revision_dictionary(self.closing_commit))

        return result

    @property
    def revisions(self):

        result = list()

        if self.status[0] == 'Closed' and self.closing_commit is not None:
            result.append(_make_revision_dictionary(self.closing_commit, {'status': 'Closed'}))

        for older, newer in zip(self.issue_snapshots[:-1], self.issue_snapshots[1:]):
            changes = dict()
            for k, v in older.data.items():
                if k not in newer.data or newer.data[k] != v:
                    changes[k] = v

            if 'hexsha' in changes:
                del changes['hexsha']

            if len(changes) > 0:
                result.append(_make_revision_dictionary(newer.commit, changes))

        original_values = self.oldest_issue_snapshot.data
        if 'hexsha' in original_values:
            del original_values['hexsha']

        result.append(_make_revision_dictionary(self.oldest_issue_snapshot.commit, original_values))

        return result

    @property
    def in_branches(self):
        result = set()
        for issue_snapshot in self.issue_snapshots:
            result.update(issue_snapshot.in_branches)
        return result

    @property
    def issue_snapshot_commit_hexshas(self):
        return [issue_snapshot.commit.hexsha for issue_snapshot in self.issue_snapshots]

    @property
    def open_in_branches(self):
        return {name for name, commit_hexsha in self.head_commits.items()
                if commit_hexsha in self.issue_snapshot_commit_hexshas}

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

    def add_snapshot(self, issue_snapshot):
        """
        Update the content of the issue history, based on newly discovered, *older* information.
        """
        self.issue_snapshots.append(issue_snapshot)
        self.issue_snapshots.sort(key=lambda issue_snapshot_in_list: issue_snapshot_in_list.date)
