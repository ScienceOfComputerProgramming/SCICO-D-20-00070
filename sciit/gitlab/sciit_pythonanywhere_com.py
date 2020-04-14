import sys

project_home = '/home/sciit/sciit/'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

from sciit.gitlab.webservice import app as application
