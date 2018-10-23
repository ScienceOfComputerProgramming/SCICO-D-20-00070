# -*- coding: utf-8 -*-
"""
Assists with running git sciit tracker commands, and is similar to any other git command. It compares
all tracked issues with issues open in the current repository or from the specified revision.

    Example:
        This module is accessed via::

            $ git sciit tracker [-h] [-a | -o | -c] [-f | -d | -n] [-s] [*revision*]

                -a, --all       
                -o, --open      
                -c, --closed    
                -f, --full      
                -d, --detailed  
                -n, --normal    
                -s, --save      
                    
"""
from sciit.cli.issue import page_history_issues
from sciit.cli.color import CPrint


def tracker(args):

    if not args.all and not args.closed and not args.open:
        args.open = True

    if not args.normal and not args.detailed and not args.full:
        args.normal = True

    if args.detailed:
        view = 'detailed'
    elif args.full:
        view = 'full'
    else:
        view = 'normal'

    args.repo.cache_issue_snapshots_from_unprocessed_commits()
    history = args.repo.get_all_issues(args.revision)
    if history:
        if args.open:
            return page_history_issues(history, view, lambda issue: issue.status[0] == 'Open')
        elif args.all:
            return page_history_issues(history, view, lambda issue: True)
        elif args.closed:
            return page_history_issues(history, view, lambda issue: issue.status[0] == 'Closed')
    else:
        CPrint.bold_green('No issues found')
