# Installation

## Command Line

Situation before installation:

    $ git sciit
    git: 'sciit' is not a git command. See 'git --help'.

Installation via pip:

    $ pip install sciit

Installation right from the source tree:

    $ python setup.py install

Now, the `git sciit` command is available::

    $ git sciit

On Unix-like systems, the installation places a `git-sciit` script into a centralised `bin` directory, which should be 
in the `PATH` environment variable.

On Windows, `git-sciit.exe` is placed into a centralised `Scripts` directory which should also be in the `PATH`.

## Gitlab Integration Service

Sciit is equipped with a Gitlab integration service, allowing issues to be synchronized between a repository on Gitlab and the Gitlab issue tracker. The service is implemented as a Flask app that can be configured to listen for webhooks from a Gitlab instance.  The following steps must be following to install the service:

1. Install the Sciit library as described above.
2. Configure your web server to serve the Gitlab integration Flask app.  An example [pythonanywhere](sciit/gitlab/sciit_pythonanywhere_com.py) WSGI configuration script is included in the repository.  The service can also be launched for *testing* purposes using the command `git sciit gitlab start` 
3. Make sure that the web server process has read/write permissions for the `~/gitlab_sites` directory.
4. Launch the application and then go to the configuration page `https://hostname/configure.