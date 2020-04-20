# -*- coding: utf-8 -*-

from sciit.cli.color import ColorPrint
from sciit.errors import EmptyRepositoryError, NoCommitsError


def init(args):
    if args.reset:
        try:
            args.repo.reset()
        except EmptyRepositoryError as error:
            ColorPrint.bold_red(error)
            return

    if not args.repo.is_init():
        args.repo.setup_file_system_resources()
        try:
            print(' ')
            if args.synchronize:
                print('Synchronising with remotes before issue repository initialisation.')
                args.repo.synchronize_with_remotes()
            ColorPrint.bold('Building repository from commits')
            args.repo.cache_issue_snapshots_from_all_commits()
            print(' ')
        except NoCommitsError as error:
            ColorPrint.yellow(error)
            ColorPrint.green('Empty issue repository created')
        except KeyboardInterrupt:
            print('\n')
            ColorPrint.bold_red('Setup issue repository process interrupted')
            print('Cleaning up')
            args.repo.reset()
            ColorPrint.yellow('Done.')
            ColorPrint.bold_yellow(' Re-run command to setup repository')
            return
    else:
        ColorPrint.green('Issue repository already setup')
        print('Use -r or --reset flag to force reset and rebuild of repository')

    return
