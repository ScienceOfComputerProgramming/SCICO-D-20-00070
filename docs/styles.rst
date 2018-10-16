.. _styles_toplevel:

Supported Files and Styles
==========================

Issue Format
------------

Issues can be created in any source code comment.  For example, in a
C style language:

.. code:: c

       /*
        * @issue create-new-user-on-client-in-db
        * @title Create New User on Client in Database
        * @description
        *  Create a new user using our command line application
        *   and register with db.
        * @label feature
        * @priority High
        * @due 12/12/2018
        */

Notice that every issue must be tagged with an `@issue` followed by a
*unique* (within a change set) identifier.

Since issues are embedded in block comments, there are different styles
of block comments and files that support those types.

C Style Languages
-----------------

Supported file extensions:

-  C/C++ files ``.c``, ``.cpp``, ``.cxx``, ``.h``, ``.hpp``, ``.hxx``
-  C# files ``.cs``
-  Java files ``.java``
-  PHP files ``.php``
-  CSS files ``.css``
-  JavaScript files ``.js``
-  SQL files ``.sql``
-  Scala files ``.scala``
-  Swift files ``.swift``
-  Go files ``.go``
-  Kotlin files ``.kt``, ``.kts``

.. code:: c

       /*
       *   @issue Eg: The title of your issue
       *   @description:
       *     A description of an issue as you
       *     want it to be even with ``markdown`` supported
       *   @issue_assigned to nystrome, kevin, daniels
       *   @due date 12 oct 2018
       *   @label in-development
       *   @weight 4
       *   @priority high
       *
       */

HTML Style
----------

Supported file extensions:

-  HTML files ``.htm``, ``.html``, ``.xhtml``
-  Markdown files ``.md``

.. code:: html

       <!--
           @issue Eg: The title of your issue
           @description:
               A description of an issue as you
               want it to be even with ``markdown`` supported
           @issue_assigned to nystrome, kevin, daniels
           @due date 12 oct 2018
           @label in-development
           @weight 4
           @priority high
       -->

Python
------

Supports ``.py`` files

.. code:: python

       """
           @issue Eg: The title of your issue
           @description:
               A description of an issue as you
               want it to be even with ``markdown`` supported
           @issue_assigned to nystrome, kevin, daniels
           @due date 12 oct 2018
           @label in-development
           @weight 4
           @priority high
       """

MATLAB
------

Supports ``.m`` files

.. code:: matlab

       %{
           @issue Eg: The title of your issue
           @description:
               A description of an issue as you
               want it to be even with ``markdown`` supported
           @issue_assigned to nystrome, kevin, daniels
           @due date 12 oct 2018
           @label in-development
           @weight 4
           @priority high
       %}

Haskell
-------

Supports ``.hs`` files

.. code:: haskell

       {-
           @issue Eg: The title of your issue
           @description:
               A description of an issue as you
               want it to be even with ``markdown`` supported
           @issue_assigned to nystrome, kevin, daniels
           @due date 12 oct 2018
           @label in-development
           @weight 4
           @priority high
       -}


Markdown
--------

Supports ``.md`` files

.. code:: markdown

       ---
           @issue Eg: The title of your issue
           @description:
               A description of an issue as you
               want it to be even with ``markdown`` supported
           @issue_assigned to nystrome, kevin, daniels
           @due date 12 oct 2018
           @label in-development
           @weight 4
           @priority high
       ---



Others
------

Supported file extensions:

-  Ruby files ``.rb``
-  BDD feature files ``.feature``
-  YAML files ``.yml``, ``.yaml``
-  Plain text files

::

       #*** (or more *)
       #   @issue Eg: The title of your issue
       #   @description:
       #       A description of an issue as you
       #       want it to be even with ``markdown`` supported
       #   @issue_assigned to nystrome, kevin, daniels
       #   @due date 12 oct 2018
       #   @label in-development
       #   @weight 4
       #   @priority high
       #*** (or more *)

For more information on how this is captured see `sciit.regex <api/sciit.regex.html>`_