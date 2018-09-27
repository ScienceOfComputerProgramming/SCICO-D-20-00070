# -*- coding: utf-8 -*-
"""
Implements the git sciit cat-file commands. Behaviour is similar to the git cat-file command but shows the
information for issue objects in our repository.

    Example:
        This command is accessed via::
        
            $ git sciit cat-file [-h] [-t] [-s] [-p] sha
"""

from sciit.errors import RepoObjectDoesNotExistError
from sciit.functions import get_repository_object_type_from_sha
from sciit import Issue, IssueCommit, IssueTree
from sciit.cli.functions import page
from sciit.cli.color import CPrint

from sciit.cli.color import Color


def cat_file(args):
    """
    Prints the content and info of objects stored in our issue repository.
    """
    try:
        object_type = get_repository_object_type_from_sha(args.repo, args.sha)
    except RepoObjectDoesNotExistError as error:
        error = f'git sciit error fatal: {error}'
        CPrint.bold_red(error)
        return

    # get object based on object type
    if object_type == 'IssueCommit':
        obj = IssueCommit.create_from_hexsha(args.repo, args.sha)
    elif object_type == 'IssueTree':
        obj = IssueTree.create_from_hexsha(args.repo, args.sha)
    elif object_type == 'Issue':
        obj = Issue.create_from_hexsha(args.repo, args.sha)

    # type flag selected
    if args.type:
        CPrint.bold(type(obj).__name__)

    # size flag selected
    elif args.size:
        CPrint.bold(obj.size)

    # print flag selected
    elif args.print:
        if type(obj) == IssueCommit:
            output = page_issue_commit(obj)
        elif type(obj) == IssueTree:
            output = page_issue_tree(obj)
        elif type(obj) == Issue:
            output = page_issue(obj)
        return output


def page_issue_commit(issue_commit):
    """
    Args:
        :(IssueCommit) icommit: commit to print to pager
    """
    time_format = '%z'
    atime = issue_commit.commit.authored_datetime.strftime(time_format)
    ctime = issue_commit.commit.committed_datetime.strftime(time_format)
    output = f'tree {issue_commit.commit.tree.hexsha}'
    output += f'\nissuetree {issue_commit.issue_tree.hexsha}'
    output += f'\nopen issues: {str(issue_commit.open_issues)}'
    for parent in issue_commit.commit.parents:
        output += f'\nparent {parent.hexsha}'
    output += f'\nauthor {issue_commit.commit.author.name}'
    output += f' <{issue_commit.commit.author.email}>'
    output += f' {str(issue_commit.commit.authored_date)} {atime}'
    output += f'\ncommiter {issue_commit.commit.committer.name}'
    output += f' <{issue_commit.commit.committer.email}>'
    output += f' {str(issue_commit.commit.committed_date)} {ctime}'
    output += f'\n\n'
    output += f'{issue_commit.commit.message}\n'

    page(output)
    return output


def page_issue_tree(issue_tree):
    """
    Args:
        :(IssueTree) itree: issue tree to print to pager
    """
    output = ''
    for issue in issue_tree.issues:
        title = issue.title
        output += f'{issue.id}\t'
        output += f'{issue.hexsha}\t'
        output += f'{title}\t'
        output += f'{issue.filepath}\n'

    page(output)
    return output


def page_issue(issue):
    """
    Args:
        :(Issue) issue: issue to print to pager
    """

    output = f'{Color.bold_yellow(f"Issue:         {issue.id}")}'
    output += f'\nTitle:         {issue.title}'
    if hasattr(issue, 'assignees'):
        output += f'\nAssigned To:   {issue.assignees}'
    if hasattr(issue, 'due_date'):
        output += f'\nDue Date:      {issue.due_date}'
    if hasattr(issue, 'label'):
        output += f'\nLabels:        {issue.label}'
    if hasattr(issue, 'weight'):
        output += f'\nWeight:        {issue.weight}'
    if hasattr(issue, 'priority'):
        output += f'\nPriority:      {issue.priority}'
    if hasattr(issue, 'filepath'):
        output += f'\nFilepath:      {issue.filepath}'
    if hasattr(issue, 'size'):
        output += f'\nSize:          {str(issue.size)}'
    if hasattr(issue, 'description'):
        output += f'\nDescription: \n{issue.description}'
    output += f'\n\n'

    page(output)
    return output
