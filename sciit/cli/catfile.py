# -*- coding: utf-8 -*-
"""Module that assists with running git sciit cat-file commands.
It is similar to the git cat-file command but shows the  
information for issue objects in our repository.

    Example:
        This command is accessed via::
        
            $ git sciit cat-file [-h] [-t] [-s] [-p] sha

@author: Nystrom Edwards

Created on 09 July 2018
"""

import json
from sciit.errors import RepoObjectDoesNotExistError
from sciit.functions import get_type_from_sha
from sciit import Issue, IssueCommit, IssueTree
from sciit.cli.functions import page_issue_commit, page_issue_tree, page_issue
from sciit.cli.color import CPrint


def catfile(args):
    """
    Prints the content and info of objects stored in our issue repository.
    """
    if not args.repo.is_init():
        CPrint.red('Repository not initialized')
        CPrint.bold_red('Run: git scitt init')
        return

    try:
        object_type = get_type_from_sha(args.repo, args.sha)
    except RepoObjectDoesNotExistError as error:
        error = 'git sciit error fatal: ' + str(error)
        CPrint.bold_red(error)
        return

    # get object based on object type
    if object_type == 'issuecommit':
        obj = IssueCommit(args.repo, args.sha)
    elif object_type == 'issuetree':
        obj = IssueTree(args.repo, args.sha)
    elif object_type == 'issue':
        obj = Issue(args.repo, args.sha)

    # type flag selected
    if args.type:
        CPrint.bold(obj.type)

    # size flag selected
    elif args.size:
        CPrint.bold(obj.size)

    # print flag selected
    elif args.print:

        if obj.type == 'issuecommit':
            output = page_issue_commit(obj)
        elif obj.type == 'issuetree':
            output = page_issue_tree(obj)
        elif obj.type == 'issue':
            output = page_issue(obj)
        return output
