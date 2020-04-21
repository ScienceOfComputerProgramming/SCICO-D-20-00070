# -*- coding: utf-8 -*-

from sciit.cli.styling import Styling
from sciit.errors import EmptyRepositoryError, NoCommitsError


def init(args):
    if args.reset:
        try:
            args.repo.reset()
        except EmptyRepositoryError as error:
            print(Styling.error_warning(error))
            return

    if not args.repo.is_init():
        args.repo.setup_file_system_resources()
        try:
            print(' ')
            if args.synchronize:
                print('Synchronising with remotes before issue repository initialisation')
                args.repo.synchronize_with_remotes()
            print('Building repository from commits')
            args.repo.cache_issue_snapshots_from_all_commits()
            print(' ')
        except NoCommitsError as error:
            print(Styling.minor_warning(error))
            print(Styling.minor_warning('Empty issue repository created'))
        except KeyboardInterrupt:
            print('\n')
            print(Styling.error_warning('Setup issue repository process interrupted'))
            print('Cleaning up...', end='')
            args.repo.reset()
            print('done.')
            print(Styling.minor_warning('Re-run command to setup issue repository'))
            return
    else:
        print(Styling.minor_warning('Issue repository already setup'))
        print(Styling.minor_warning('Use -r or --reset flag to force reset and rebuild of repository'))

    return
