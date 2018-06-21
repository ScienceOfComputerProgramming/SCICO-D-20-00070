
__all__ = ('EmptyRepositoryError', 'NoCommitsError')


class EmptyRepositoryError(FileNotFoundError):
    def __init__(self):
        super().__init__('The issue repository is empty.')


class NoCommitsError(FileNotFoundError):
    def __init__(self):
        super().__init__('The repository has no commits.')
