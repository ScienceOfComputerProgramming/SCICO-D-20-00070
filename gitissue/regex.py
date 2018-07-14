# -*- coding: utf-8 -*-
"""Module that contains the definition regex patterns used to identify issues
in source code.

:@author: Nystrom Edwards
:Created: 24 June 2018
"""

CSTYLE = r'/\*((?:.|[\r\n])*?)\*/'
PYTHON = r'(?:=\s*(?:[\'\"]){3}(?:.*(?:.|[\r\n])*?)(?:[\'\"]){3})|(?:[\'\"]){3}(.*(?:.|[\r\n])*?)(?:[\'\"]){3}'
C = CSTYLE
CPP = CSTYLE
JAVA = CSTYLE
CSHARP = CSTYLE
PHP = CSTYLE
CSS = CSTYLE
JAVASCRIPT = CSTYLE
SQL = CSTYLE
SCALA = CSTYLE
HTML = r'<!--((?:(?:.|[\r\n])*?))-->'
MATLAB = r'%{((?:.|[\r\n])*?)%}'
HASKELL = r'{-((?:.|[\r\n])*?)-}'
RUBY = r'=begin((?:(?:.|[\r\n])*?))[\r\n]{1}=end'


class ISSUE:
    TITLE = r'@(?:[Ii]ssue[ _-]*)+(?:[Tt]itle)* *[=:;>]*(.*)'
    DESCRIPTION = r'@(?:[Ii]ssue[ _-]*)*[Dd]escription* *[-=:;> ]*(.*(?:.|[\r\n])*?)(?:\n[\s]*@|$)'
    ASSIGNEES = r'@(?:[Ii]ssue[ _-]*)*[Aa]ssign(?:ed|ees|ee)*(?:[ _-]to)* *[-=:;> ]* (.*)'
    DUE_DATE = r'@(?:[Ii]ssue[ _-]*)*[Dd]ue[ _-]*(?:[Dd]ate)* *[-=:;> ]* (.*)'
    LABEL = r'@(?:[Ii]ssue[ _-]*)*(?:[Ll]abel(?:s)?|[Tt]ag(?:s)?)+ *[-=:;> ]* (.*)'
    WEIGHT = r'@(?:[Ii]ssue[ _-]*)*[Ww]eight *[=:;> ]*(.*)'
    PRIORITY = r'@(?:[Ii]ssue[ _-]*)*[Pp]riority *[=:;> ]*(.*)'
