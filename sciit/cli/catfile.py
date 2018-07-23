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
from sciit.cli.functions import print_issue_commit, print_issue_tree, print_issue


def cat(args):
    """
    Prints the content and info of objects stored in our issue repository.
    """

    try:
        object_type = get_type_from_sha(args.repo, args.sha)
    except RepoObjectDoesNotExistError as error:
        error = 'git sciit error fatal: ' + str(error)
        print(error)
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
        print(obj.type)

    # size flag selected
    elif args.size:
        print(obj.size)

    # print flag selected
    elif args.print:

        if obj.type == 'issuecommit':
            print_issue_commit(obj)
        elif obj.type == 'issuetree':
            print_issue_tree(obj)
        elif obj.type == 'issue':
            print_issue(obj)