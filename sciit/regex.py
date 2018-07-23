# -*- coding: utf-8 -*-
"""Module that contains the definition regex patterns used to identify issues
in source code.

:@author: Nystrom Edwards
:Created: 24 June 2018
"""
import os

CSTYLE = r'/\*((?:.|[\r\n])*?)\*/'
PYTHON = r'(?:=\s*(?:[\'\"]){3}(?:.*(?:.|[\r\n])*?)(?:[\'\"]){3})|(?:[\'\"]){3}(.*(?:.|[\r\n])*?)(?:[\'\"]){3}'
HTML = r'<!--((?:(?:.|[\r\n])*?))-->'
MATLAB = r'%{((?:.|[\r\n])*?)%}'
HASKELL = r'{-((?:.|[\r\n])*?)-}'
RUBY = r'=begin((?:(?:.|[\r\n])*?))[\r\n]{1}=end'


CSTYLE_EXTS = ['.java', '.c', '.cpp', '.cxx', '.h', '.hpp', '.hxx', '.cs', '.php',
               '.css', '.js', '.sql', '.scala', '.swift', '.go', '.kt', '.kts']
HTML_EXTS = ['.htm', '.html', '.xhtml']


class ISSUE:
    TITLE = r'@(?:[Ii]ssue[ _-]*)+(?:[Tt]itle)* *[=:;>]*(.*)'
    DESCRIPTION = r'@(?:[Ii]ssue[ _-]*)*[Dd]escription* *[-=:;> ]*(.*(?:.|[\r\n])*?)(?:\n[\s]*@|$)'
    ASSIGNEES = r'@(?:[Ii]ssue[ _-]*)*[Aa]ssign(?:ed|ees|ee)*(?:[ _-]to)* *[-=:;> ]* (.*)'
    DUE_DATE = r'@(?:[Ii]ssue[ _-]*)*[Dd]ue[ _-]*(?:[Dd]ate)* *[-=:;> ]* (.*)'
    LABEL = r'@(?:[Ii]ssue[ _-]*)*(?:[Ll]abel(?:s)?|[Tt]ag(?:s)?)+ *[-=:;> ]* (.*)'
    WEIGHT = r'@(?:[Ii]ssue[ _-]*)*[Ww]eight *[=:;> ]*(.*)'
    PRIORITY = r'@(?:[Ii]ssue[ _-]*)*[Pp]riority *[=:;> ]*(.*)'

def get_file_object_pattern(file_object):
    # get file extension and set pattern
    ext = os.path.splitext(file_object.path)[1]
    if ext is not '':
        if ext in CSTYLE_EXTS:
            pattern = CSTYLE
        elif ext in HTML_EXTS:
            pattern = HTML
        elif ext == '.m':
            pattern = MATLAB
        elif ext == '.hs':
            pattern = HASKELL
        elif ext == '.py':
            pattern = PYTHON
        elif ext == '.rb':
            pattern = RUBY
        else:
            pattern = False
    elif file_object.mime_type != 'text/plain' \
            or 'markdown' in file_object.mime_type:
        pattern = False
    else:
        pattern = None

    return pattern