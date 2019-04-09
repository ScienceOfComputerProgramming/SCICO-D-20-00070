---
@issue eliminate-repeated-subprocess-creation-during-init
@title Eliminate Repeated Subprocess Creation During Init
@description
The init command repeatedly calls commit::find_branches_for_commit() which repeatedly spawns git sub-processes.  This is very expensive.  It would be better if a single sub-process was called once the first time find_branches_for_commit wsas created and then the association between all commits and branches retrieved and cached once.
---
