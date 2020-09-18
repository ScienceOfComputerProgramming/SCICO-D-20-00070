# Command Line Usage

```bash
git-scitt | git sciit | git-sciit.exe <command> <options>
```

## Init

```bash
git sciit init [-r | --reset]
```

Creates an empty repository or builds from past commits.

`[--reset | -r]` Removes all existing issue repository artifacts, including git hooks and cached issue snapshot database before rebulding.

## Status

```bash
git sciit status [-f | -n] [revision]
```

Shows the user how many issues are open and how many are closed on all branches.

`[--full | -f]` Shows a table of open and closed issues.

`[--normal | -n]` Shows a count of open and closed issues.

## Log

```bash
git sciit log [revision]
```

Outputs a log that is similar to the git command, but includes a summary of open issues for each commit.

`[revision]` The git revision path to use to control logging.

## Issue

```bash
git scitt issue <issue_id> [-f | -n ] issueid [revision]
```

Shows information about the issue with the given id.

`[--full | -f]` Shows the full history of changes to the issue.

`[--normal | -n]` Shows the normal summary of the current state of the issue.

## New

```bash
git sciit new [-p | -a]
```

Creates a new issue in the project backlog on a branch specified by the issue id.

Prompts user for:

 * Issue title
 * Issue id or default slug of issue title
 * File path for markdown file or default to backlog folder
 * A description of the issue
 * A commit message for creating the issue

`[--push | -p]` Pushes the newly created issue branch to the origin.

`[--accept | -a]` Accepts the newly created issue branch by merging it to master locally.

## Close (Experimental)

```git sciit close 
git sciit close <issue_id>
```

Removes the issue from all branches it is present in within the current repository.  The effect within Sciit is to change the issue status to Closed.

## Web

```bash
git sciit web
```

Launches the web interface for viewing issue information.

## Tracker

```bash
git scitt tracker [-a | -o | -c ] [-f | -n ]  [revision]
```

Prints a log that shows issues and their status.

`[--full | -f]` Shows the full history of changes to the issues.

`[--normal | -n]` Shows the normal summary of the current state of the issues.

`[revision]` The git revision path to use to control the view of the issues.

## Gitlab

### Start

```bash
git scitt gitlab start 

```

Launches the gitlab webservice that integrates Gitlab issues with sciit.  Used primarily for testing the Gitlab 
integration service.  The command must be run in the parent directory of `gitlab-sites`. 

### Reset

```bash
git scitt gitlab reset project_url sites_local_path
```

Resets the issue tracker database and rebuild from past commits.

`project_url` The URL of the project to be managed by Gitlab

`sites_local_path` The path to the local gitlab sites mirror directory


### Set credentials

```bash
git sciit gitlab set_credentials project_url gitlab_username web_hook_secret_token api_token sites_local_path
```

Sets a gitlab username, web hook token and API token for a Gitlab project to be  used by the sciit gitlab service.
Primarily used for debugging purposes by integration service Admins.  The configuration process is largely automated
by the Gitlab integration service configure page. (see [INSTALL.md](./INSTALL.md).)

`project_url` The URL of the project to be managed by Gitlab

`gitlab_username` The Gitlab account username that will manage the Gitlab issue tracker and repository
  synchronisation.  The account should *not* be that of an actual developer on the project.

`web_hook_secret_token` Token set on the Gitlab repository to authenticate incoming Webhook events.

`api_token` Token set on the Gitlab user account to provide access to the Gitlab API.

`sites_local_path` The path to the local gitlab sites mirror directory
