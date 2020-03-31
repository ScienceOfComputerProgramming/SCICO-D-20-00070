# -*- coding: utf-8 -*-

import os
import mimetypes


C_STYLE = r'/\*((?:.|[\r\n])*?)\*/'
PYTHON = r'(?:=\s*(?:[\'\"]){3}(?:.*(?:.|[\r\n])*?)(?:[\'\"]){3})|(?:[\'\"]){3}(.*(?:.|[\r\n])*?)(?:[\'\"]){3}'

HTML = r'(?:<!--)([\w\W]+?)(?:-->)'

MATLAB = r'%{((?:.|[\r\n])*?)%}'
HASKELL = r'{-((?:.|[\r\n])*?)-}'
PLAIN = r'#(?:[*]){3,}((?:(?:.|[\r\n])*?))#(?:[*]){3,}'
MARKDOWN = r'(?:---)([\w\W]+?)(?:---)'

C_STYLE_FILE_EXTENSIONS = \
    ['.java', '.c', '.cpp', '.cxx', '.h', '.hpp', '.hxx', '.cs', '.php', '.css', '.js', '.sql', '.scala', '.swift',
     '.go', '.kt', '.kts']

HTML_FILE_EXTENSIONS =\
    ['.htm', '.html', '.xhtml']

OTHER_FILE_EXTENSIONS =\
    ['.yml', '.yaml', '.feature', '.rb']

MARKDOWN_FILE_EXTENSIONS = ['.md']


# noinspection SpellCheckingInspection
class IssuePropertyRegularExpressions:
    ID = r'@[Ii]ssue[ _-]*(?:id|number|slug)* *[=:;>]*(.*)'
    TITLE = r'@(?:[Ii]ssue[ _-]*)*[Tt]itle *[=:;>]*(.*)'
    DESCRIPTION = r'@(?:[Ii]ssue[ _-]*)*[Dd]escription* *[-=:;> ]*(.*(?:.|[\r\n])*?)(?:\n[\s]*@|$)'
    ASSIGNEES = r'@(?:[Ii]ssue[ _-]*)*[Aa]ssign(?:ed|ees|ee)*(?:[ _-]to)* *[-=:;> ]* (.*)'
    DUE_DATE = r'@(?:[Ii]ssue[ _-]*)*[Dd]ue[ _-]*(?:[Dd]ate)* *[-=:;> ]* (.*)'
    LABEL = r'@(?:[Ii]ssue[ _-]*)*(?:[Ll]abel(?:s)?|[Tt]ag(?:s)?)+ *[-=:;> ]* (.*)'
    WEIGHT = r'@(?:[Ii]ssue[ _-]*)*[Ww]eight *[=:;> ]*(.*)'
    BLOCKERS = r'@(?:[Ii]ssue[ _-]*)*[Bb]lockers *[=:;> ]*(.*)'
    PRIORITY = r'@(?:[Ii]ssue[ _-]*)*[Pp]riority *[=:;> ]*(.*)'


class IssuePropertyReplacementRegularExpressions:

    @staticmethod
    def title(issue_id):
        return f'(@[Ii]ssue[ _-]*(?:id|number|slug)* *[=:;>]*(?:{issue_id})(?:.|[\r\n])*?(?:@[Ii]ssue[ _-])* *[Tt]itle *[=:;>]*)(.*)'

    @staticmethod
    def description(issue_id):
        return f'(@[Ii]ssue[ _-]*(?:id|number|slug)* *[=:;>]*(?:{issue_id})(?:.|[\r\n])*?@(?:[Ii]ssue[ _-]*)*[Dd]escription *[=:;>]*)(.*(?:.|[\r\n])*?)((?:.*$)|(?:.*@|$))'


def get_comment_leading_char(pattern):
    if pattern in (PYTHON, HTML, MATLAB, HASKELL):
        return ''
    elif pattern == C_STYLE:
        return '*'
    elif pattern == PLAIN:
        return '#'
    else:
        return ''


def get_file_object_pattern(path, mime_type=None):
    ext = os.path.splitext(path)[1]

    _mime_type = mimetypes.guess_type(path) if mime_type is None else mime_type

    if ext is not '':
        if ext in C_STYLE_FILE_EXTENSIONS:
            pattern = C_STYLE
        elif ext in HTML_FILE_EXTENSIONS:
            pattern = HTML
        elif ext in MARKDOWN_FILE_EXTENSIONS:
            pattern = MARKDOWN
        elif ext == '.m':
            pattern = MATLAB
        elif ext == '.hs':
            pattern = HASKELL
        elif ext == '.py':
            pattern = PYTHON
        elif ext in OTHER_FILE_EXTENSIONS or _mime_type == 'text/plain':
            pattern = PLAIN
        else:
            pattern = False
    elif _mime_type == 'text/plain':
        pattern = PLAIN
    else:
        pattern = False

    return pattern
