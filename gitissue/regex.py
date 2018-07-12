# -*- coding: utf-8 -*-
"""Module that contains the definition regex patterns used to identify issues
in source code.

:@author: Nystrom Edwards
:Created: 24 June 2018
"""

PYTHON_MULTILINE_DOCSTRING = r'\s(?:[\'\"]){3}(.*(?:.|[\r\n])*?)(?:[\'\"]){3}'


class ISSUE:
    NUMBER = r'@[Ii]ssue[ _-]*(?:id|number|no)* *[-=:;> ]*[#]*([^\s]+)'
    TITLE = r'@(?:[Ii]ssue[ _-]*)*[Tt]itle *[-=:;> ]*(.*)'
    DESCRIPTION = r'@(?:[Ii]ssue[ _-]*)*[Dd]escription* *[-=:;> ]*(.*(?:.|[\r\n])*?)(?:\n[\s]*@|$)'
    ASSIGNEES = r'@(?:[Ii]ssue[ _-]*)*[Aa]ssign(?:ed|ees|ee)*(?:[ _-]to)* *[-=:;> ]* (.*)'
    DUE_DATE = r'@(?:[Ii]ssue[ _-]*)*[Dd]ue[ _-]*(?:[Dd]ate)* *[-=:;> ]* (.*)'
    LABEL = r'@(?:[Ii]ssue[ _-]*)*(?:[Ll]abel(?:s)?|[Tt]ag(?:s)?)+ *[-=:;> ]* (.*)'
    WEIGHT = r'@(?:[Ii]ssue[ _-]*)*[Ww]eight *[=:;> ]*(.*)'
    PRIORITY = r'@(?:[Ii]ssue[ _-]*)*[Pp]riority *[=:;> ]*(.*)'
