# -*- coding: utf-8 -*-

import os

CSTYLE = r'/\*((?:.|[\r\n])*?)\*/'
PYTHON = r'(?:=\s*(?:[\'\"]){3}(?:.*(?:.|[\r\n])*?)(?:[\'\"]){3})|(?:[\'\"]){3}(.*(?:.|[\r\n])*?)(?:[\'\"]){3}'

HTML = r'(?:<!--)([\w\W]+?)(?:-->)'

MATLAB = r'%{((?:.|[\r\n])*?)%}'
HASKELL = r'{-((?:.|[\r\n])*?)-}'
PLAIN = r'#(?:[*]){3,}((?:(?:.|[\r\n])*?))#(?:[*]){3,}'
MARKDOWN = r'(?:---)([\w\W]+?)(?:---)'

CSTYLE_EXTS = ['.java', '.c', '.cpp', '.cxx', '.h', '.hpp', '.hxx', '.cs', '.php',
               '.css', '.js', '.sql', '.scala', '.swift', '.go', '.kt', '.kts']
HTML_EXTS = ['.htm', '.html', '.xhtml']
OTHER_EXTS = ['.yml', '.yaml', '.feature', '.rb']
MARKDOWN_EXTS = ['.md']


class ISSUE:
    ID = r'@[Ii]ssue[ _-]*(?:id|number|slug)* *[=:;>]*(.*)'
    TITLE = r'@(?:[Ii]ssue[ _-]*)*[Tt]itle *[=:;>]*(.*)'
    DESCRIPTION = r'@(?:[Ii]ssue[ _-]*)*[Dd]escription* *[-=:;> ]*(.*(?:.|[\r\n])*?)(?:\n[\s]*@|$)'
    ASSIGNEES = r'@(?:[Ii]ssue[ _-]*)*[Aa]ssign(?:ed|ees|ee)*(?:[ _-]to)* *[-=:;> ]* (.*)'
    DUE_DATE = r'@(?:[Ii]ssue[ _-]*)*[Dd]ue[ _-]*(?:[Dd]ate)* *[-=:;> ]* (.*)'
    LABEL = r'@(?:[Ii]ssue[ _-]*)*(?:[Ll]abel(?:s)?|[Tt]ag(?:s)?)+ *[-=:;> ]* (.*)'
    WEIGHT = r'@(?:[Ii]ssue[ _-]*)*[Ww]eight *[=:;> ]*(.*)'
    PRIORITY = r'@(?:[Ii]ssue[ _-]*)*[Pp]riority *[=:;> ]*(.*)'


def get_file_object_pattern(file_object):
    ext = os.path.splitext(file_object.path)[1]
    print(ext)
    if ext is not '':
        if ext in CSTYLE_EXTS:
            pattern = CSTYLE
        elif ext in HTML_EXTS:
            pattern = HTML
        elif ext in MARKDOWN_EXTS:
            pattern = MARKDOWN
        elif ext == '.m':
            pattern = MATLAB
        elif ext == '.hs':
            pattern = HASKELL
        elif ext == '.py':
            pattern = PYTHON
        elif ext in OTHER_EXTS or file_object.mime_type == 'text/plain':
            pattern = PLAIN
        else:
            pattern = False
    elif file_object.mime_type == 'text/plain':
        pattern = PLAIN
    else:
        pattern = False

    return pattern
