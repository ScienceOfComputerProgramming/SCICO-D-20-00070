---
@issue add-capability-for-comments
@title Add Capability for Comments
@description
We need a mechanism for storing comments within an issue.  The proposal is that a comment can be added to an issue using the 
@comment annotation.

For example, a comment could be added like this:

    @comment from Tim
    What about large comment threads? What about multiple threads.

If there are too many comments then these can be placed in a separate file, say in a directory called comment-threads, for example:

    @comment-thread comment-threads/add-capability-for-comments.md

Both these tags could be used multiple times inside an issue.  The responsibility would be on the developer for ensuring that
comments appear in a sensible order.

The sciit user interface could re-construct the actual ordering using the commit time of the first appearance of a comment. 
If a comment is removed during a commit then it could be treated as deleted and appear in the transcript as such.  Also, if a 
comment is by an unknown user, e.g. Tim, then this could be labelled as a pseudonym for the user handle, e.g. twsswt.

---
