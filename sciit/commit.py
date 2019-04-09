# -*- coding: utf-8 -*-

import re
import subprocess
import shutil

from sciit import IssueSnapshot
from sciit.regex import PLAIN, CSTYLE, ISSUE, get_file_object_pattern


__all__ = 'find_issues_in_commit'


def _get_files_changed_in_commit(commit):
    result = set()
    for key in set(commit.stats.files.keys()):
        if ' => ' in key:
            # Handle for file rename key format.
            if '{' in key:
                prefix = key.split('{')[0]
                postfix = key.split('}')[1]

                change = key.split('{')[1].split('}')[0].split(' => ')
                source_file = prefix + change[0] + postfix
                destination_file = prefix + change[1] + postfix

                result.add(destination_file)
                result.add(source_file)
            else:
                paths = key.split(' => ')
                source_path = paths[0]
                destination_path = paths[1]
                result.add(source_path)
                result.add(destination_path)
        else:
            result.add(key)
    return result


def get_blobs_from_commit_tree(tree):
    blobs = {blob.path: blob for blob in tree.blobs}
    for tree in tree.trees:
        blobs.update(get_blobs_from_commit_tree(tree))
    return blobs


def find_issue_in_comment(comment: str):

    issue = dict()

    def update_issue_data_dict_with_value_from_comment(regex, key):
        value = re.findall(regex, comment)
        if len(value) > 0:
            issue[key] = value[0].rstrip()

    update_issue_data_dict_with_value_from_comment(ISSUE.ID, 'issue_id')

    if 'issue_id' in issue:
        update_issue_data_dict_with_value_from_comment(ISSUE.TITLE, 'title')
        update_issue_data_dict_with_value_from_comment(ISSUE.DESCRIPTION, 'description')
        update_issue_data_dict_with_value_from_comment(ISSUE.ASSIGNEES, 'assignees')
        update_issue_data_dict_with_value_from_comment(ISSUE.LABEL, 'label')
        update_issue_data_dict_with_value_from_comment(ISSUE.DUE_DATE, 'due_date')
        update_issue_data_dict_with_value_from_comment(ISSUE.PRIORITY, 'priority')
        update_issue_data_dict_with_value_from_comment(ISSUE.WEIGHT, 'weight')
        update_issue_data_dict_with_value_from_comment(ISSUE.BLOCKERS, 'blockers')

    return issue


def find_issues_in_blob(comment_pattern, blob_content):
    comments = re.findall(comment_pattern, blob_content)
    comments_with_issues = [x for x in comments if re.search(ISSUE.ID, x) is not None]

    issues = list()

    for comment in comments_with_issues:
        if comment_pattern == PLAIN:
            comment = re.sub(r'^\s*#', '', comment, flags=re.M)
        if comment_pattern == CSTYLE:
            comment = re.sub(r'^\s*\*', '', comment, flags=re.M)
        issue = find_issue_in_comment(comment)
        if issue:
            issues.append(issue)

    return issues


def read_in_blob_contents(blob):
    blob_contents = blob.data_stream.read()
    if type(blob_contents) == bytes:
        try:
            return blob_contents.decode("utf-8")
        except UnicodeDecodeError:
            return None
    else:
        return blob_contents


def find_issue_snapshots_in_commit_paths_that_changed(commit, comment_pattern=None, ignore_files=None):
    issue_snapshots = list()

    files_changed_in_commit = _get_files_changed_in_commit(commit)
    blobs = get_blobs_from_commit_tree(commit.tree)

    if ignore_files:
        files_changed_in_commit -= set(ignore_files.match_files(files_changed_in_commit))

    in_branches = _find_branches_for_commit(commit)

    for file_changed in files_changed_in_commit:
        # Handles deleted files they won't exist.
        if file_changed not in blobs:
            continue

        blob = blobs[file_changed]

        _comment_pattern = get_file_object_pattern(blob) if not comment_pattern else comment_pattern

        if not _comment_pattern:
            continue

        blob_contents = read_in_blob_contents(blob)
        if blob_contents is None:
            continue

        blob_issues = find_issues_in_blob(_comment_pattern, blob_contents)

        for issue_data in blob_issues:
            issue_data['filepath'] = file_changed
            issue_snapshot = IssueSnapshot(commit, issue_data, in_branches)
            issue_snapshots.append(issue_snapshot)

    return issue_snapshots, files_changed_in_commit, in_branches


_commit_branches_cache = None


def _get_commit_branches_from_subprocess(command, script):
    sub_process = subprocess.Popen([command], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    (process_out, process_err) = sub_process.communicate(script)
    return process_out


def _get_commit_branches_from_bash():
    bash_script = \
        b"""
        declare -A COMMIT_BRANCHES

        BRANCHES=(`git branch -a |tr '*' ' ' ` )

        for BRANCH in ${BRANCHES[@]}
        do
            COMMITS=( `git log --format="%H" $BRANCH` )
            for COMMIT in ${COMMITS[@]}
            do
            if [ -v "COMMIT_BRANCHES[$COMMIT]" ]
            then
                COMMIT_BRANCHES[$COMMIT]="${COMMIT_BRANCHES[$COMMIT]},$BRANCH"
            else
                COMMIT_BRANCHES[$COMMIT]="$BRANCH"
            fi
            done;
        done

        for COMMIT in ${!COMMIT_BRANCHES[@]}
        do
            echo $COMMIT:${COMMIT_BRANCHES[$COMMIT]} 
        done
        """

    return _get_commit_branches_from_subprocess("bash", bash_script)


def _get_commit_branches_from_powershell():
    power_shell_script = \
        b"""
        $branches = git branch -a
        $branches = $branches.Trim("*", " ")

        $commit_branches = @{}

        foreach ($branch in $branches) {
          $commits = git log --format="%H" $branch
          foreach ($commit in $commits){
            if ($commit_branches.ContainsKey($commit)){
              $commit_branches[$commit] = "$($commit_branches[$commit]),$branch"
            } else {
              $commit_branches[$commit] = $branch
            }
          }
        }

        foreach($commit in $commit_branches.keys){
          echo $commit_branches[$commit]
        }
        """
    return _get_commit_branches_from_subprocess("powershell.exe", power_shell_script)


def _init_commit_branch_cache():
    global _commit_branches_cache
    _commit_branches_cache = dict()

    if shutil.which('bash') is not None:
        sub_process_out = _get_commit_branches_from_bash()
    else:
        sub_process_out = _get_commit_branches_from_powershell()

    for line in sub_process_out.decode("utf-8").strip().split('\n'):
        commit_str, branches_str = line.split(':')
        branches = branches_str.split(',')
        _commit_branches_cache[commit_str] = branches


def _find_branches_for_commit(commit):
    global _commit_branches_cache
    if not _commit_branches_cache:
        _init_commit_branch_cache()
    return _commit_branches_cache[commit.hexsha]

