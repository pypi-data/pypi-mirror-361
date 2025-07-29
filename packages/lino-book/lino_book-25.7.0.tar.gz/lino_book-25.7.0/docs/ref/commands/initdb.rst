.. doctest docs/ref/commands/initdb.rst

=====================================
``initdb`` : initialize your database
=====================================

.. management_command:: initdb

The :manage:`initdb` command is one of Lino's utilities for providing
application-specific demo data.  It performs an initialization of the database,
replacing all data by default data loaded from the specified fixtures.

This command removes *all existing tables* from the database (not only Django
tables), then runs Django's :manage: `migrate` to create all tables, followed by
Django's :manage:`loaddata` command to load the specified fixtures.
and finally runs :cmd:`pm buildcache`.

The :manage:`initdb` command performs three actions in one:

- it flushes the database specified in your :xfile:`settings.py`,
  i.e. issues a ``DROP TABLE`` for every table used by your application.

- it runs Django's :manage:`migrate` command to re-create all tables,

- it runs Django's :manage:`loaddata` command to load the specified
  fixtures.

For example the command

::

  $ python manage.py initdb std demo demo2

is functionally equivalent to the following series of :cmd:`django-admin`
commands::

  $ python manage.py flush
  $ python manage.py migrate
  $ python manage.py loaddata std demo demo2
  $ python manage.py buildcache

The main difference is that :manage:`initdb` doesn't ask you to type
"yes" followed by :kbd:`RETURN` in order to confirm that you really
want it.  Yes, removing all tables may sound dangerous, but it *is*
actually what we want quite often: when we just want to quickly try
this application, or when we are developing a prototype and made some
changes to the database structure.


It also adds a `warning filter
<https://docs.python.org/3/library/warnings.html#warning-filter>`__ to ignore
Django's warnings about empty fixtures. (See :djangoticket:`18213`).

It reimplements a simplified version of Django's `reset` command, without the
possibility of deleting *only some* data (the thing which caused so big problems
that Django 1.3. decided to `deprecate this command
<https://docs.djangoproject.com/en/5.0/releases/1.3\
/#reset-and-sqlreset-management-commands>`__.

Deleting all data and table definitions from a database is not always
trivial. It is not tested on PostgreSQL. In MySQL we use a somewhat
hackerish and MySQL-specific DROP DATABASE and CREATE DATABASE because
even with `constraint_checks_disabled` we had sporadic errors. See
:blogref:`20150328`

We usually don't use Django's migration framework, so :manage:`initdb` runs
Django's `migrate` command with the `--run-syncdb
<https://docs.djangoproject.com/en/5.0/ref/django-admin/#django-admin-option---run-syncdb>`_
option, which "allows creating tables for apps without migrations". The Django
docs add that "While this isn't recommended, the migrations framework is
sometimes too slow on large projects with hundreds of models."  Yes, that's why
we go the non-recommended way :-)


See also the :cmd:`pm prep` command and :doc:`/dev/demo_fixtures`.

.. program:: pm initdb

Options:

.. option:: --noinput

  Do not prompt for user input of any kind.

.. option:: --removemedia

  Remove all files in the :setting:`MEDIA_ROOT` directory.

..
  Do not build the site cache. Skip the call to :cmd:`pm buildcache`.
  This is used by the :xfile:`restore.py` script because during a :ref:`site
  upgrade <admin.upgrade>` it can happen that the maintainer needs to call
  :xfile:`restore.py` multiple times in order to migrate the database, while
  :cmd:`pm buildcache` needs to be run only once.


.. include:: /../docs/shared/include/tested.rst

>>> import lino
>>> lino.startup('lino_book.projects.min1.settings')
>>> from lino.api.doctest import *
>>> from atelier.sheller import Sheller
>>> shell = Sheller(settings.SITE.project_dir)

>>> shell("django-admin initdb --help")
... #doctest: +NORMALIZE_WHITESPACE +ELLIPSIS +REPORT_UDIFF
usage: django-admin initdb [-h] [--noinput] [--removemedia] [--database DATABASE] [--version]
                           [-v {0,1,2,3}] [--settings SETTINGS] [--pythonpath PYTHONPATH]
                           [--traceback] [--no-color] [--force-color] [--skip-checks]
                           [fixtures ...]
<BLANKLINE>
positional arguments:
  fixtures              the fixtures to load
<BLANKLINE>
options:
  -h, --help            show this help message and exit
  --noinput             Do not prompt for input of any kind.
  --removemedia         Remove all files in the settings.MEDIA_ROOT directory.
  --database DATABASE   Nominates a database to reset. Defaults to the "default" database.
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
  --skip-checks         Skip system checks.
