# Installation

## Requirements

Sciit requires Python 3.7 or later and Git 2.26 or later to build, install and run successfully.
python3 (not python) and git must be in executable from be locatable by env.

## Command Line

Situation before installation:

    $ git sciit
    git: 'sciit' is not a git command. See 'git --help'.

Installation right from the source tree:

    $ python setup.py install

Now, the `git sciit` command is available:

    $ git sciit

On Unix-like systems, the installation places a `git-sciit` script into a centralised `bin` directory, which should be 
in the `PATH` environment variable.

On Windows, `git-sciit.exe` is placed into a centralised `Scripts` directory which should also be in the `PATH`.

## Gitlab Integration Service

Sciit is equipped with a Gitlab integration service, allowing issues to be synchronized between a repository on Gitlab 
and the Gitlab issue tracker. The service is implemented as a Flask app that can be configured to listen for webhooks
from a Gitlab instance.

The service requires a sub-directory to exist wherever the integration service web application is launched from with 
read and write access to called `gitlab-sites`.  In the pythonanywhere example, the directory is assumed to be at 
`/home/sciit/sciit/gitlab-sites`.  This directory is used to store mirrors of repositories on Gitlab that 
are synchronised by the integration service.
 
The following steps must be following to install the service:

1. Install the Sciit library as described above.
2. Configure your web server to serve the Gitlab integration Flask app.  An example 
   [pythonanywhere](sciit/gitlab/sciit_pythonanywhere_com.py) WSGI configuration script is included in the repository.
    The service can also be launched for *testing* purposes using the command `git sciit gitlab start` from the 
    parent directory of `gitlab-sites`.  More information on configuring WSGI for Apache is available
     [here](https://modwsgi.readthedocs.io/en/develop/user-guides/quick-configuration-guide.html) and for nginx
      [here](https://uwsgi-docs.readthedocs.io/en/latest/Nginx.html).
3. Make sure that the web server process has read/write permissions for the `~/gitlab_sites` directory.
4. Launch the application and then go to the configuration page `https://hostname/configure.
