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
from sciit.cli.issue import page_history_items
from sciit.cli.color import CPrint
from sciit.functions import cache_history


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

    args.repo.sync()

    if args.open:
        history = args.repo.get_open_issues(args.revision)
    elif args.all:
        history = args.repo.get_all_issues(args.revision)
    elif args.closed:
        history = args.repo.get_closed_issues(args.revision)
    else:
        history = None

    if history:
        if args.save:
            cache_history(args.repo.issue_dir, history)
            CPrint.bold('Issues saved to ' +
                        args.repo.issue_dir + '/HISTORY\n')
        else:
            output = page_history_items(history, view)
            return output
    else:
        CPrint.bold_green('No issues found')