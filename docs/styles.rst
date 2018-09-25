.. _styles_toplevel:

Supported Files and Styles
==========================

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
       *   @issue id-of-your-issue-slugified
       *   @title The title of the issue
       *   @description
       *     A description of an issue as you
       *     want it to be even with ``markdown`` supported
       *   @assignees nystrome, kevin, daniels
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

.. code:: html

       <!--
           @issue id-of-your-issue-slugified
           @title The title of the issue
           @description
               A description of an issue as you
               want it to be even with ``markdown`` supported
           @assignes nystrome, kevin, daniels
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
           @issue id-of-your-issue-slugified
           @title The title of the issue
           @description
               A description of an issue as you
               want it to be even with ``markdown`` supported
           @assignes nystrome, kevin, daniels
           @due date 12 oct 2018
           @label in-development
           @weight 4
           @priority high
       """
       
Markdown
--------

Supports ``.md`` files

.. code::

       ---
           @issue id-of-your-issue-slugified
           @title The title of the issue
           @description
               A description of an issue as you
               want it to be even with ``markdown`` supported
           @assignees nystrome, kevin, daniels
           @due date 12 oct 2018
           @label in-development
           @weight 4
           @priority high
       ---

MATLAB
------

Supports ``.m`` files

.. code:: matlab

       %{
           @issue id-of-your-issue-slugified
           @title The title of the issue
           @description
               A description of an issue as you
               want it to be even with ``markdown`` supported
           @assignes nystrome, kevin, daniels
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
           @issue id-of-your-issue-slugified
           @title The title of the issue
           @description
               A description of an issue as you
               want it to be even with ``markdown`` supported
           @assignees nystrome, kevin, daniels
           @due date 12 oct 2018
           @label in-development
           @weight 4
           @priority high
       -}

Others
------

Supported file extensions:

-  Ruby files ``.rb``
-  BDD feature files ``.feature``
-  YAML files ``.yml``, ``.yaml``
-  Plain text files

::

       #*** (or more *)
       #   @issue id-of-your-issue-slugified
       #   @title The title of the issue
       #   @description
       #       A description of an issue as you
       #       want it to be even with ``markdown`` supported
       #   @assignees nystrome, kevin, daniels
       #   @due date 12 oct 2018
       #   @label in-development
       #   @weight 4
       #   @priority high
       #*** (or more *)

For more information on how this is captured see `sciit.regex <api/sciit.regex.html>`_