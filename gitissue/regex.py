# -*- coding: utf-8 -*-
"""Module that contains the definition regex patterns used to identify issues
in source code.

:@author: Nystrom Edwards
:Created: 24 June 2018
"""

MULTILINE_HASH_PYTHON_COMMENT = r'((?:#.*(?:\n\s*#)*.*)|(?:#.*)|(?:#.*$))'
