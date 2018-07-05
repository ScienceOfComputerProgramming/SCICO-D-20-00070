# -*- coding: utf-8 -*-
"""Module that contains the definition regex patterns used to identify issues
in source code.

:@author: Nystrom Edwards
:Created: 24 June 2018
"""

PYTHON_MULTILINE_HASH = r'#((?:.*(?:[\r\n]\s*#)*.*)|(?:#.*)|(?:#.*$))'
PYTHON_MULTILINE_DOCSTRING = r'(?:[\'\"]){3}(.*(?:.|[\r\n])*?)(?:[\'\"]){3}'

PART_OF_EXISTING_ISSUE = r'@[Ii]ssue[ _-]*(?:id|number)* *[=:;>]*(?:.|[\r\n])*'

ISSUE_NUMBER = r'@[Ii]ssue[ _-]*(?:id|number|no)* *[-=:;>]*(.*)'
ISSUE_TITLE = PART_OF_EXISTING_ISSUE + \
    r'@(?:[Ii]ssue[ _-]*)*[Tt]itle *[-=:;>]*(.*)'
ISSUE_DESCRIPTION = PART_OF_EXISTING_ISSUE + \
    r'@(?:[Ii]ssue[ _-]*)*[Dd]escription* *[-=:;>]*(.*(?:.|[\r\n])*?)(?:\n@|$)'
ISSUE_ASSIGNEES = PART_OF_EXISTING_ISSUE + \
    r'@(?:[Ii]ssue[ _-]*)*[Aa]ssign(?:ed|ees|ee)*(?:[ _-]to)* *[-=:;>]* (.*)'
ISSUE_DUE_DATE = PART_OF_EXISTING_ISSUE + \
    r'@(?:[Ii]ssue[ _-]*)*[Dd]ue[ _-]*(?:[Dd]ate)* *[-=:;>]* (.*)'
ISSUE_LABEL = PART_OF_EXISTING_ISSUE + \
    r'@(?:[Ii]ssue[ _-]*)*(?:[Ll]abel(?:s)?|[Tt]ag(?:s)?)+ *[-=:;>]* (.*)'
ISSUE_WEIGHT = PART_OF_EXISTING_ISSUE + \
    r'@(?:[Ii]ssue[ _-]*)*[Ww]eight *[=:;>]*(.*)'
ISSUE_PRIORITY = PART_OF_EXISTING_ISSUE + \
    r'@(?:[Ii]ssue[ _-]*)*[Pp]riority *[=:;>]*(.*)'
