import unittest.mock


class SubprocessRun():

    class Simple(unittest.mock.Mock):
        stdout = b'output'

    class GitPass(unittest.mock.Mock):
        stdout = b'usage: git'

    class GitFail(unittest.mock.Mock):
        stdout = b'fatal: not a git repository'
