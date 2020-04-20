# Sciit: Source Control Integrated Issue Tracker

## Description

Current state of the art software project issue tracking tools, such as GitHub, GitLab, JIRA and Trac store issues separately from the version control repository that contains the project's source code. This creates _friction_, because software developers must remember to keep both the issue tracker and the version control repository up to date as progress is made on completing tasks.

Sciit solves this problem by providing an interface for managing issues that are stored _within_ the source code maintained in the version repository. This has a number of advantages for eliminating friction:

- The package that an issue refers to can be identified implicitly, by storing the issue in the most relevant sub-directory of the code base.
- The assignee and other contributors to an issue and its resolution can be identified based on who is making commits to a
  repository.
- Implicit links can be identified between source code affected by an issue, if both the issue and the source code are altered in a single change set.
- Comments on issues can be automatically recovered from the version control log.

SCIIT is equipped with a command line user interface for managing the SCIIT installation process for a git repository.  It also has commands for reviewing issues and for launching a demonstrator web based user interface.


## Basic Usage

Issues can be created anywhere in your source code as block comments in the underlying programming language format. The comment then becomes part of a trackable versioned object within your git repository. Commit, merge and checkout operations done by git will run git hooks installed by Sciit in the background in order to automate issue tracking.

An example of a recommended style for Java:

```java
    /*
    * @issue the-title-of-your-issue
    * @title The title of your issue
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

Notice that every issue must be tagged with an `@issue` followed by a *unique* (within a change set) identifier.

The command `git sciit new` can be used to generate a new issue in a markdown file and in a branch with a name that matches that of the issue, following a proposed Sciit workflow extension to git-flow.

Since issues are embedded in block comments, there are different styles of block comments and files that support those types.

Installation instructions can be found [here](INSTALL.md)

More styles and supported files can be found [here](STYLES.md)

Command line interaction instructions can be found [here](COMMAND.md)

## Other Distributed Issue Trackers

There are a number of other tools that embed issue tracking into source control
management. Many thanks to Jan De Muijnck-Hughes and the anonymous ICSME 2019 reviewer who added to this list.

 * Bug: https://github.com/driusan/bug
 * Bugs Everywhere: http://www.bugseverywhere.org/
 * Fossil: http://www.fossil-scm.org/
 * Git-bug: https://github.com/MichaelMure/git-bug
 * Git-dit: https://github.com/neithernut/git-dit
 * Git Issue: https://github.com/dspinellis/git-issue
 * Issue: https://github.com/marekjm/issue
 * Mercurial's B Extension: https://www.mercurial-scm.org/wiki/bExtension
 * Ticgit: https://github.com/jeffWelling/ticgit
 * Veracity: http://veracity-scm.com/compare/
   

