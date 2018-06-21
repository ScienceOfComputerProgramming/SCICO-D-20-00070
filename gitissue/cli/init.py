from gitissue import tools


def init(args):

    if args.reset:
        args.repo.reset()

    if not args.repo.is_init():
        args.repo.setup

        if tools.yes_no_option('Build issue repository from past commits'):
            args.repo.build()
    else:
        print('Issue repository already setup')
        # except KeyboardInterrupt:
        #         # TODO raise error here
        #         raise()
        # print(' ')
        # print('Setup issue repository process interupted')
        # print('Cleaning up')
        # self.reset()
        # print('Done')
        # sys.exit(0)

    return
