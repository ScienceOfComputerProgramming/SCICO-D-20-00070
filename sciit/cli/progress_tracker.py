from datetime import datetime


def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=50, fill='#'):
    """
    From https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console

    Args:
       :(int) iteration: current iteration
       :(int) total: total iterations
       :(str) prefix: prefix string
       :(str) suffix: suffix string
       :(str) decimals: positive number of decimals in percent complete
       :(int) length: character length of bar
       :(str) fill: bar fill character
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    progress_bar = fill * filled_length + '-' * (length - filled_length)

    print('\r%s |%s| %s%% %s' % (prefix, progress_bar, percent, suffix), end='\r')

    if iteration == total:
        print()


class ProgressTracker(object):
    def __init__(self, cli, number_of_commits_for_processing):
        self.cli = cli
        self.number_of_commits_for_processing = number_of_commits_for_processing
        self.commits_scanned = 0
        self.start = datetime.now()

    def processed_commit(self):
        self.commits_scanned += 1
        self._print_commit_progress()

    def _print_commit_progress(self):
        if self.cli:
            duration = datetime.now() - self.start
            commits_scanned = self.commits_scanned
            number_of_commits_for_processing = self.number_of_commits_for_processing

            prefix = 'Processing %d/%d commits: ' % (commits_scanned, number_of_commits_for_processing)
            suffix = ' Duration: %s' % str(duration)

            print_progress_bar(commits_scanned, number_of_commits_for_processing, prefix=prefix, suffix=suffix)
