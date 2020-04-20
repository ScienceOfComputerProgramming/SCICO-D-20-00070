# -*- coding: utf-8 -*-

import os
import mimetypes
import re

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


def get_issue_property_regex(key):
    mapping = {
        'title': IssuePropertyRegularExpressions.TITLE,
        'due_date': IssuePropertyRegularExpressions.DUE_DATE,
        'labels': IssuePropertyRegularExpressions.LABEL,
        'weight': IssuePropertyRegularExpressions.WEIGHT,
        'priority': IssuePropertyRegularExpressions.PRIORITY
    }
    return mapping[key] if key in mapping else None


def add_comment_chars(comment_pattern, issue_string, indent):
    if comment_pattern == MARKDOWN:

        comment_string = "\n".join([indent + line for line in issue_string.split('\n')])

        return "---\n" + comment_string + "\n---"

    elif comment_pattern == C_STYLE:
        comment_string = "\n".join([indent + '* ' + line for line in issue_string.strip().split('\n')])
        return indent[0:-2] + "/**\n" + comment_string + "\n" + indent + "**/"


# noinspection SpellCheckingInspection
def strip_comment_chars(comment_pattern, comment_string):

    if comment_pattern == PLAIN:
        indent_re = '([\t| ]+)#([\t| ]+)@(?:[Ii]ssue)'
        indent_match = re.search(indent_re, comment_string)
        indent = indent_match.group(1) if indent_match else ''

        return re.sub(r'^\s*#\s*', '', comment_string, flags=re.M), indent

    if comment_pattern == C_STYLE:

        indent_re = '([\t| ]+)\*([\t| ]+)@(?:[Ii]ssue)'
        indent_match = re.search(indent_re, comment_string)
        indent = indent_match.group(1)

        stripped_content = comment_string
        stripped_content = re.sub(r'^\s*/\**', '', stripped_content)  # Start marker
        stripped_content = re.sub(r'[ \t\r\f\v]*\**/\s*$', '', stripped_content)  # End marker
        stripped_content = re.sub(r'^\s*\*[ \t\r\f\v]*', '', stripped_content, flags=re.M)

        return stripped_content, indent

    if comment_pattern == PYTHON:
        indent_re = '([\t| ]+)@(?:[Ii]ssue)'
        indent_match = re.search(indent_re, comment_string)
        if indent_match is not None:
            indent = indent_match.group(1)
        else:
            indent = ''

        issue_string = re.search(r'([\'"])\1\1(.*?)\1{3}', comment_string, re.DOTALL).group(2).strip()
        return issue_string, indent
        # return comment_string[3:-3], indent

    elif comment_pattern == MARKDOWN:
        indent_re = '([\t| ]+)@(?:[Ii]ssue)'
        indent_match = re.search(indent_re, comment_string)
        if indent_match is not None:
            indent = indent_match.group(1)
        else:
            indent = ''

        issue_string = re.search(MARKDOWN, comment_string).group(1).strip()
        return issue_string, indent

    else:
        return comment_string, ''


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
