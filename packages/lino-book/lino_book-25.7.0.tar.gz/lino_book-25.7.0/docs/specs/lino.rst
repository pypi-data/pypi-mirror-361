.. doctest docs/specs/lino.rst
.. include:: /../docs/shared/include/defs.rst
.. _specs.lino:

==================================
``lino`` : Lino core functionality
==================================

The :mod:`lino` package is automatically installed as a plugin on every
:term:`Lino site`. It doesn't add any database model, but a series of
:term:`django-admin commands <django-admin command>` and the translations for
messages of the :mod:`lino` package.

.. currentmodule:: lino

.. contents::
   :depth: 1
   :local:

.. include:: /../docs/shared/include/tested.rst

>>> import lino
>>> lino.startup('lino_book.projects.min1.settings')
>>> from lino.api.doctest import *
>>> from atelier.sheller import Sheller
>>> shell = Sheller(settings.SITE.project_dir)

.. _specs.lino.admin_commands:

The `django-admin` commands added by the ``lino`` plugin
========================================================

The source code of these commands is in the :mod:`lino.management.commands`
package.

See also :doc:`/ref/commands/index`.


Useful commands
---------------

.. management_command:: demotest

  Run a series of standard read-only tests in this project.

  Unlike :manage:`test` this command not create a temporary database, it uses
  the demo database content populated by :cmd:`pm prep`. So it assumes that
  :cmd:`pm prep` has run successfully.

  These tests use the Django test client to simulate a :manage:`runserver`
  followed some browser requests. They log in once with every user. This causes
  e.g. the JS cache files to get generated if necessary.


.. management_command:: install

Run 'pip install --upgrade' for all Python packages required by this site.

>>> shell("django-admin install --help")  #doctest: +NORMALIZE_WHITESPACE
usage: django-admin install [-h] [--noinput] [-l] [--version] [-v {0,1,2,3}]
                            [--settings SETTINGS] [--pythonpath PYTHONPATH] [--traceback]
                            [--no-color] [--force-color]
<BLANKLINE>
Run 'pip install --upgrade' for all Python packages required by this site.
<BLANKLINE>
options:
  -h, --help            show this help message and exit
  --noinput             Do not prompt for input of any kind.
  -l, --list            Just list the requirements, don't install them.
  --version             Show program's version number and exit.
  -v {0,1,2,3}, --verbosity {0,1,2,3}
                        Verbosity level; 0=minimal output, 1=normal output, 2=verbose output,
                        3=very verbose output
  --settings SETTINGS   The Python path to a settings module, e.g. "myproject.settings.main".
                        If this isn't provided, the DJANGO_SETTINGS_MODULE environment
                        variable will be used.
  --pythonpath PYTHONPATH
                        A directory to add to the Python path, e.g.
                        "/home/djangoprojects/myproject".
  --traceback           Display a full stack trace on CommandError exceptions.
  --no-color            Don't colorize the command output.
  --force-color         Force colorization of the command output.


.. management_command:: qtclient

Run a Qt client for this :term:`site <Lino site>`.  See :doc:`/dev/qtclient`.

.. management_command:: diag

  Write a diagnostic status report about this site.

This is a command-line shortcut for calling
:meth:`lino.core.site.Site.diagnostic_report_rst`.

This is deprecated. You should use :manage:`status` instead.


.. management_command:: show

  Show the content of a specified table to standard output.


.. management_command:: resetsequences

Reset the database sequences for all plugins.

This is required (and automatically called) on a postgres after
restoring from a snapshot (:xfile:`restore.py`) because this operation
specifies explicit primary keys.

Unlike Django's :manage:`sqlsequencereset` command this does not just
output the SQL statements, it also executes them.  And it works always
on all plugins so you don't need to specify their names.

This is functionally equivalent to the following::

  python manage.py sqlsequencereset APP1 APP2... | python manage.py shell

On SQLite or MySQL this command does nothing.

In PostgreSQL, Sequence objects are special single-row tables created
with CREATE SEQUENCE. Sequence objects are commonly used to generate
unique identifiers for rows of a table (exceprt from `PostgreSQL docs
<https://www.postgresql.org/docs/current/static/functions-sequence.html>`__).

See :blogref:`20170907`, :blogref:`20170930`.


.. management_command:: makemigdump

Create a dump for migration tests.

Calls :cmd:`pm dump2py` to create python dump in a
`tests/dumps/<version>` directory. See :doc:`/dev/migtests`


Experimental commands
---------------------

.. management_command:: mergedata

Takes the full name of a python module as argument. It then imports
this module and expects it to define a function `objects` in its
global namespace. It calls this function and expects it to yield a
series of Django instance objects which have not yet been saved. It
then compares these objects with the "corresponding data" in the
database and prints a summary to stdout. It then suggests to merge the
new data into the database.

- It never *deletes* any stored records.
- All incoming objects either replace an existing (stored) object, or
  will be added to the database.
- If an incoming object has a non-empty primary key, then it replaces
  the corresponding stored object. Otherwise, if the model has
  `unique` fields, then these cause potential replacement.

Currently the command is only partly implemented, it doesn't yet
update existing records.  But it detects whether records are new, and
adds only those.

.. management_command:: monitor

  Experimental work. Don't use this.
  Writes a status report about this Site.
  Used to monitor a production database.


Historical commands
-------------------


.. management_command:: configure

    Old name for :manage:`install`.


.. management_command:: initdb_demo

    Old name for :cmd:`pm prep`.


Translation texts
=================

All translatable texts of the :mod:`lino` package are stored below
:file:`lino/locale`.
