# Command Line Usage

```bash
git-scitt | git sciit | git-sciit.exe <command> <options>
```

## Init

`git sciit init [-r | --reset]

Creates an empty repository or builds from past commits.

`[--reset | -r]` Removes all existing issue repository artifacts, including git hooks and cached issue snapshot database before rebulding.

## Log

`git sciit log [revision]`

Outputs a log that is similar to the git command, but includes a summary of open issues for each commit.

`[revision]` The git revision path to use to control logging.

## Issue

`git scitt issue [-f | -d | -n ] issueid [revision]`

Shows information about the issue with the given id.

`[--full | -f]` Shows the full history of changes to the issue.
`[--detailed | -d]` Shows the detailed view of the  issue, including a summary of commits the issue was present in.
`[--normal | -n]` Shows the normal summary of the current state of the issue.

## Web

``git sciit web`

Launches the web interface for viewing issue information.

## Tracker

`git scitt tracker [-a | -o | -c ] [-f | -d | -n ]  [revision]`

`[--full | -f]` Shows the full history of changes to the issues.
`[--detailed | -d]` Shows the detailed view of the  issues, including a summary of commits the issues wer present in.
`[--normal | -n]` Shows the normal summary of the current state of the issues.

`[revision]` The git revision path to use to control the view of the issues.

