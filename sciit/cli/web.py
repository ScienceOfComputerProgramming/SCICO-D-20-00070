from sciit.web.server import launch as launch_web_service


def launch(args):
    launch_web_service(args.repo)
