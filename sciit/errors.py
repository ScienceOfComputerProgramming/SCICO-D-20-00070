# -*- coding: utf-8 -*-


class EmptyRepositoryError(FileNotFoundError):
    def __init__(self):
        super().__init__('The issue repository is empty.')


class NoCommitsError(FileNotFoundError):
    def __init__(self):
        super().__init__('The repository has no commits.')


class RepoObjectExistsError(FileExistsError):
    def __init__(self):
        super().__init__('The repository object already exists.')


class RepoObjectDoesNotExistError(FileNotFoundError):
    def __init__(self, filename):
        super().__init__('The repository object [%s] does not exist.' % filename)
