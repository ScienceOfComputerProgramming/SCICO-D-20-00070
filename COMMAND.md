# Command Line Usage

```bash
git-scitt | git sciit | git-sciit.exe <command> <options>
```

## Common options

`[--help | -h]`  show the help message and exit

`[revision]` the revision path to use to generate the issue log e.g. 'all' for all commits or 'master' for all commit on
master branch or 'HEAD~2' from the last two commits on current branch. See `git rev-list` options for more path options

`[--full | -f]` view the full  information for issues including, description, commit activity, multiple file paths, 
open in, and found in branches

`[--normal | -n]` default: view summary issue information


## Init

```bash
git sciit init [-r | -s]
```

Creates an empty repository or builds from past commits.

`[--reset | -r]` resets the issue repo and rebuild from past commits

`[--synchronize | -s]` synchronizes repository with remotes before initialisation


## Status

```bash
git sciit status [-f | -n] [revision]
```

Shows the user how many issues are open and how many are closed on all branches.


## Log

```bash
git sciit log [revision]
```

shows a log that is similar to the git log but shows open issues


## Issue

```bash
git scitt [-f | -n ] issue_id [revision]
```

shows information about the issue with the given id


## New

```bash
git sciit new [-p | -a]
```

creates a new issue in the project backlog on a branch specified by the issue id

Prompts user for:

 * Issue title
 * Issue id or default slug of issue title
 * File path for markdown file or default to backlog folder
 * A description of the issue
 * A commit message for creating the issue

`[--push | -p]` pushes the newly created issue branch to the origin

`[--accept | -a]` accepts the newly created issue branch by merging it to master locally


## Close (Experimental)

```git sciit close 
git sciit close issue_id
```

closes an issue in the current branch
  
The effect within Sciit is to change the issue status to Closed.


## Web

```bash
git sciit web
```

launches a local web interface for the sciit issue tracker


## Tracker

```bash
git scitt tracker [-a | -o | -c ] [-f | -n ]  [revision]
```

prints a log that shows issues and their status

`[--all | -a]` show all the issues currently tracked and their status

`[-o | --open]`  default: show only issues that are open

`[-c | --closed]`  show only issues that are closed


## Gitlab

### Start

```bash
git scitt gitlab start 

```

launches the gitlab webservice that integrates Gitlab issues with sciit

Used primarily for testing the Gitlab integration service.  The command must be run in the parent directory of 
`gitlab-sites`. 


### Reset

```bash
git scitt gitlab reset project_url sites_local_path
```

resets the issue tracker database and rebuild from past commits

`project_url` The URL of the project to be managed by Gitlab

`sites_local_path` The path to the local gitlab sites mirror directory


### Set credentials

```bash
git sciit gitlab set_credentials project_url gitlab_username web_hook_secret_token api_token sites_local_path
```

Sets a gitlab username, web hook token and API token for a Gitlab project to be  used by the sciit gitlab service

Primarily used for debugging purposes by integration service Admins.  The configuration process is largely automated
by the Gitlab integration service configure page. (see [INSTALL.md](./INSTALL.md).)

`project_url` The URL of the project to be managed by Gitlab

`gitlab_username` The Gitlab account username that will manage the Gitlab issue tracker and repository
  synchronisation.  The account should *not* be that of an actual developer on the project.

`web_hook_secret_token` Token set on the Gitlab repository to authenticate incoming Webhook events.

`api_token` Token set on the Gitlab user account to provide access to the Gitlab API.

`sites_local_path` The path to the local gitlab sites mirror directory
