.. _tested_docs:
.. _dev.doctest:

================
Doctests in Lino
================

The :ref:`book` repository contains over 1000 documentation pages, many of which
are :term:`tested documents <tested document>`.

.. glossary::

  tested document

    A documentation page that contain blocks of Python code ("code snippets")
    marked by a ``>>>`` in the beginning of each line, and which is getting
    tested using Python's `doctest
    <https://docs.python.org/3/library/doctest.html>`__ command as part of a
    test suite.

The :cmd:`doctest` command extracts code snippets from any text file, executes
them and checks whether their output is the same as the one displayed in the
document.

When you want to run :cmd:`doctest` examples for testing Lino application code,
you need  specify a :term:`Django settings module` to tell :cmd:`doctest` which
:term:`demo project` your code snippets are to run in.

Here is an example of how you do that:

>>> from lino import startup
>>> startup('lino_book.projects.min1.settings')

Calling :func:`lino.startup` in a tested doc will trigger the :term:`site
startup` and is the equivalent of starting a  Django :manage:`shell` in the
given demo project::

  $ go min1
  $ pm shell

In such a Django :manage:`shell` session you can re-play the instructions on
such pages interactively (when your :doc:`developer environment is installed
</dev/install/index>`)

The first thing you usually say in a Django shell and in a tested doc is:

>>> from lino.api.doctest import *

The :mod:`lino.api.doctest` is *by definition* everything we want to have in the
global namespace of a tested document.

Some demo projects have a :xfile:`startup.py` script with above three lines of
code.

.. xfile:: startup.py

  A script in a :term:`demo project` that contains above-mentioned three lines
  of code and gets imported from doctests. Besides calling :func:`lino.startup`
  it may do assertions to ensure that the database content hasn't been modified
  e.g. by some other doctest.



How they are tested
===================

The test suite of a repository with tested documents has a file
:xfile:`test_docs.py` in its :file:`tests` directory.

.. xfile:: test_docs.py

The :xfile:`test_docs.py` calls
:func:`atelier.test.make_docs_suite` to automatically create a unit test for
every document in the doctree. A simple :xfile:`test_docs.py` file looks like
this::

  from atelier.test import make_docs_suite

  def load_tests(loader, standard_tests, pattern):
      suite = make_docs_suite("docs")
      return suite

The initialization code usually imports and calls :func:`lino.startup`, then
imports everything (``*``) from  the :mod:`lino.api.doctest` module (which
contains a selection of the most frequently used commands used in doctests).


They require of course that the :term:`demo project` has been populated
previously by :cmd:`inv prep`, not on a temporary test database as the Django
test runner creates it.

The advantage of this method (compared to using the Django test runner) is that
they don't need to populate the database (load the demo fixtures) for each test
run. A limitation of this method is of course that they may not modify the
database. That's why we sometimes call them static or passive. They just observe
whether everything looks as expected.  When you want to test something that
modifies the database, you don't write a tested document but a Django test case.


See also:

- :mod:`atelier.test`
- :mod:`lino.utils.pythontest` and :mod:`lino.utils.djangotest`
- :mod:`lino.utils.test`
