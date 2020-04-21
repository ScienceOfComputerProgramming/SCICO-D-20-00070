# -*- coding: utf-8 -*-

from termcolor import colored


class Styling:

    white_background = False

    """
    Adds colour and highlights to .
    """
    @classmethod
    def error_warning(cls, string):
        if Styling.white_background:
            return colored(string, 'white', on_color='on_red', attrs=['bold'])
        else:
            return colored(string, 'red', attrs=['bold'])

    @classmethod
    def minor_warning(cls, string):
        if Styling.white_background:
            return colored(string, 'blue', attrs=['bold', 'dark'])
        else:
            return colored(string, 'yellow', attrs=['bold'])

    @classmethod
    def closed_status(cls, string):
        if Styling.white_background:
            return colored(string, 'white', on_color='on_red', attrs=['bold'])
        else:
            return colored(string, 'red', attrs=['bold'])

    @classmethod
    def open_status(cls, string):
        if Styling.white_background:
            return colored(string, 'white', on_color='on_green', attrs=['bold'])
        else:
            return colored(string, 'green', attrs=['bold'])

    @classmethod
    def item_title(cls, string):
        if Styling.white_background:
            return colored(string, 'blue', attrs=['bold', 'dark', 'underline'])
        else:
            return colored(string, 'yellow', attrs=['bold', 'underline'])

    @classmethod
    def item_subtitle(cls, string):
        if Styling.white_background:
            return colored(string, 'blue', attrs=['bold', 'dark'])
        else:
            return colored(string, 'yellow', attrs=['bold'])

    @classmethod
    def bold_yellow(cls, string):
        return colored(string, 'blue', attrs=['bold'])

