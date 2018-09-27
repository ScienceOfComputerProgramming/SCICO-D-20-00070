# -*- coding: utf-8 -*-

from termcolor import colored


class Color:
    """A simple class wrapper that helps to add color to strings
    """

    @classmethod
    def red(cls, string):
        return(colored(string, 'red'))

    @classmethod
    def green(cls, string):
        return(colored(string, 'green'))

    @classmethod
    def yellow(cls, string):
        return(colored(string, 'yellow'))

    @classmethod
    def bold(cls, string):
        return(colored(string, attrs=['bold']))

    @classmethod
    def bold_red(cls, string):
        return(colored(string, 'red', attrs=['bold']))

    @classmethod
    def bold_green(cls, string):
        return(colored(string, 'green', attrs=['bold']))

    @classmethod
    def bold_yellow(cls, string):
        return(colored(string, 'yellow', attrs=['bold']))


class CPrint:
    """A simple class wrapper that helps to print messages to the
    shell terminals
    """

    @classmethod
    def red(cls, string):
        print(colored(string, 'red'))

    @classmethod
    def green(cls, string):
        print(colored(string, 'green'))

    @classmethod
    def yellow(cls, string):
        print(colored(string, 'yellow'))

    @classmethod
    def bold(cls, string):
        print(colored(string, attrs=['bold']))

    @classmethod
    def bold_red(cls, string):
        print(colored(string, 'red', attrs=['bold']))

    @classmethod
    def bold_green(cls, string):
        print(colored(string, 'green', attrs=['bold']))

    @classmethod
    def bold_yellow(cls, string):
        print(colored(string, 'yellow', attrs=['bold']))
