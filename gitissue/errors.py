# -*- coding: utf-8 -*-
"""Module that contains the erros that may be raised
when using the library.

:@author: Nystrom Edwards
:Created: 21 June 2018
"""

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
    def __init__(self):
        super().__init__('The repository object does not exist.')
