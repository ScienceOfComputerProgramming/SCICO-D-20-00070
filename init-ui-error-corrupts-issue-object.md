---
@issue init-ui-error-corrupts-issue-object
@title An Error in init -r User Interface Causes Issue Object to be Corrupted
@description:
  If init -r is invoked on a non-compatible share, e.g. Cygwin, it causes
  a char mode mapping error.  This then causes the overall process to fail,
  corrupting the issue object in the repository.  It would be better if the
  old cache was, well cached, while a new instance is rebuilt and then
  replaced only if the rebuild is successful.

@priority low
---
