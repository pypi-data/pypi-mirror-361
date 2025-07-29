.. doctest docs/ref/commands/prep.rst
.. include:: /../docs/shared/include/defs.rst

===============================================
``prep`` : load initial data into your database
===============================================

.. program:: pm prep
.. command:: pm prep

Flush the database and load the default demo fixtures.

Used to create your database and populate it with some demo content.

Calls :manage:`initdb` using the site's
:attr:`lino.core.site.Site.demo_fixtures` as arguments.

This command is defined by the :mod:`lino` core plugin. It is just a thin
wrapper that calls :cmd:`pm initdb` with a default list of fixtures to load.


Options:

.. option:: -b
.. option:: --batch
.. option:: --noinput

    Do not prompt for user input of any kind.

.. option:: --verbosity

  The verbosity level (0=minimal output, 1=normal output, 2=verbose output,
  3=very verbose output). :command:`pm prep` forwards this option to
  :command:`pm initdb`.

.. option:: --keepmedia

  Do NOT remove media files.

  :command:`pm prep` adds the :option:`pm initdb --removemedia` option when
  calling  :command:`pm initdb`.  In a :term:`developer environment` you usually
  want :command:`pm prep` to remove any media files. But for example on a
  :term:`demo server` you can call :option:`--keepmedia <pm prep --keepmedia>`
  if you DON'T want :command:`pm prep` to remove them.





.. include:: /../docs/shared/include/tested.rst

>>> import lino
>>> lino.startup('lino_book.projects.min1.settings')
>>> from lino.api.doctest import *
>>> from atelier.sheller import Sheller
>>> shell = Sheller(settings.SITE.project_dir)

>>> shell("django-admin prep --help")  #doctest: +NORMALIZE_WHITESPACE +ELLIPSIS +REPORT_UDIFF
usage: django-admin prep [-h] [-b] [--keepmedia] [--version] [-v {0,1,2,3}]
                         [--settings SETTINGS] [--pythonpath PYTHONPATH] [--traceback]
                         [--no-color] [--force-color] [--skip-checks]
<BLANKLINE>
Flush the database and load the default demo fixtures.
<BLANKLINE>
options:
  -h, --help            show this help message and exit
  -b, --batch, --noinput
                        Do not prompt for input of any kind.
  --keepmedia           Do not remove media files.
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
