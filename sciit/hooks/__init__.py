"""
@issue bug on reset
@title Resetting commits pose an issue with showing recent IssueCommits
@description
    There is no hook in git that runs post-reset. Since IssueCommits are built
    on top of commits, when commits are reset the HEAD for IssueCommits remain
    at the top of the previous object. These leads to a RepoObjectDoesNotExistError
    at least until the user creates another commit and the both repositories are
    in sync.

    Possible Solution:
    
    * Try to find a better way to iter_issue_commits from the latest git commit head
"""
