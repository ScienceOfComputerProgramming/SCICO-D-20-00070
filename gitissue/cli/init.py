import sys
from gitissue import tools
from gitissue.errors import EmptyRepositoryError, NoCommitsError


def init(args):

    if args.reset:
        try:
            args.repo.reset()
        except EmptyRepositoryError as error:
            print(error)

    if not args.repo.is_init():
        args.repo.setup()

        if args.yes or tools.yes_no_option('Build issue repository from past commits'):
            try:
                print(' ')
                print('Building repository from commits')
                args.repo.build()
                print(' ')
            except NoCommitsError as error:
                print(error)
                print('Empty issue repository created')
            except KeyboardInterrupt:
                print(' ')
                print('Setup issue repository process interupted')
                print('Cleaning up')
                args.repo.reset()
                print('Done')
                sys.exit(0)
        else:
            print('Empty issue repository created')
    else:
        print('Issue repository already setup')

    return
