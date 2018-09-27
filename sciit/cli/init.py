# -*- coding: utf-8 -*-
"""
Assists with creating a git sciit repository. It contains functions that allows the creation of an empty repository or
to create a repository from source code comments in past commits. It is similar to the git init command but  helps build
 issues for existing repositories.

    Example:
        This command is accessed via::
        
            $ git sciit init [-h] [-r] [-y]
"""

from sciit.cli.color import CPrint
from sciit.errors import EmptyRepositoryError, NoCommitsError


def init(args):
    if args.reset:
        try:
            args.repo.reset()
        except EmptyRepositoryError as error:
            CPrint.bold_red(error)
            return

    if not args.repo.is_init():
        args.repo.setup_file_system_resources()
        try:
            print(' ')
            CPrint.bold('Building repository from commits')
            args.repo.build_issue_commits_from_all_commits()
            print(' ')
        except NoCommitsError as error:
            CPrint.yellow(error)
            CPrint.green('Empty issue repository created')
        except KeyboardInterrupt:
            print('\n')
            CPrint.bold_red('Setup issue repository process interupted')
            print('Cleaning up')
            args.repo.reset()
            CPrint.yellow('Done.')
            CPrint.bold_yellow(' Re-run command to setup repository')
            return
    else:
        CPrint.green('Issue repository already setup')
        print('Use -r or --reset flag to force reset and rebuild of repository')

    return