# Source Control Integrated Issue Tracker

## Description

Current state of the art software project issue tracking tools, such as GitHub, GitLab, JIRA and Trac store issues separately from the version control repository that contains the project's source code. This creates _friction_, because software developers must remember to keep both the issue tracker and the version control repository up to date as progress is made on completing tasks. The aim of this project is to develop a system for managing issues that are stored within the source code of the version repository. This has a number of advantages for eliminating friction:

- The package that an issue refers to can be identified implicitly, by storing the issue in the most relevant sub-directory of the code base.
- The assignee for an issue can be identified based on who is making commits to a
  repository.
- Implicit links can be identified between source code affected by an issue, if both the issue and the source code are altered in a single change set.
- Comments on issues can be automatically recovered from the version control log.

## Objectives

The aim of this project is to develop a demonstrator application or plugin for existing software project management tools that allow issues to be managed _within_ a version control repository rather than as a separate database.

# Instructions

This application manages software development issues within your git repository.
It is structured as a Python command line applications.

## Usage

To use the application you can create your issues anywhere in your source code as block comments in a particular format and it will become a trackable versioned object within your git environment. Operations done with git will run git sciit in the background in order to automate issue tracking for you.

An example of a recommended style for Java:

```java
    /*
    * @issue Eg: The title of your issue
    * @description:
    *   A description of an issue as you
    *   want it to be even with markdown supported
    * @issue_assigned to nystrome, kevin, daniels
    * @due date 12 oct 2018
    * @label in-development
    * @weight 4
    * @priority high
    *
    */
```

More styles and supported files can be found [here](STYLES.md)

Cheat sheet of commands can be found [here](docs/Cheatsheet.png)


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

On Unix-like systems, the installation places a `git-sciit` script into a centralised `bin` directory, which should be in your `PATH`.

On Windows, `git-sciit.exe` is placed into a centralised `Scripts` directory which
should also be in your `PATH`.
