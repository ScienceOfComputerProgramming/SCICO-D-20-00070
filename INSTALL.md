# Installation

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
