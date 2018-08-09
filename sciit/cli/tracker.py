# -*- coding: utf-8 -*-
"""Module that assists with running git sciit tracker commands.
This is in no way similar to any other git command. It compares
all tracked issues with issues open in the current repository 
or from the specified revision.

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
                    
@author: Nystrom Edwards

Created on 10 July 2018
"""
from git.exc import GitCommandError
from sciit.cli.functions import page_history_items
from sciit.cli.color import CPrint
from sciit.errors import NoCommitsError, RepoObjectDoesNotExistError
from sciit.functions import cache_history


def tracker(args):
    """
    Prints a log that shows issues and their status based on the
    flags specified
    """
    if not args.repo.is_init():
        CPrint.red('Repository not initialized')
        CPrint.bold_red('Run: git scitt init')
        return

    # force open if no flags supplied
    if not args.all and not args.closed and not args.open:
        args.open = True

    # force normal if no flags supplied
    if not args.normal and not args.detailed and not args.full:
        args.normal = True

    if args.normal:
        view = 'normal'
    elif args.detailed:
        view = 'detailed'
    elif args.full:
        view = 'full'

    try:
        args.repo.sync()
        # open flag selected
        if args.open:
            history = args.repo.get_open_issues(args.revision)
        # all flag selected
        elif args.all:
            history = args.repo.get_all_issues(args.revision)
        # closed flag selected
        elif args.closed:
            history = args.repo.get_closed_issues(args.revision)
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
    except NoCommitsError as error:
        error = f'git sciit error fatal: {str(error)}'
        CPrint.bold_red(error)
        return
    except GitCommandError as error:
        error = f'git sciit error fatal: bad revision \'{args.revision}\''
        CPrint.bold_red(error)
        return
    except RepoObjectDoesNotExistError as error:
        CPrint.bold_red(error)
        print('Solve error by rebuilding issue repository using: git sciit init -r')
        return
