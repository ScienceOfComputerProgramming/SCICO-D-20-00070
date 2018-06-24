from gitissue.tools import yes_no_option


def log(args):
    if(yes_no_option('Do you want to see the issue log')):
        print('Shows the log of issues')
    return
