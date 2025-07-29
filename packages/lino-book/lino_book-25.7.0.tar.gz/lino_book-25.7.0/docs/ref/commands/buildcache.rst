.. doctest docs/ref/commands/buildcache.rst

=====================================
``buildcache`` : build the site cache
=====================================

Build the files in your :term:`site cache` and run :cmd:`pm collectstatic`.


.. command:: pm buildcache

.. program:: pm buildcache

Usage
=====

For example::

  $ pm buildcache -b

This command also defines :option:`-b` or :option:`--batch` as aliases for
:option:`--noinput`. The advantage is that after running :xfile:`pull.sh` you
can type :cmd:`pm buildcache -b` rather than waiting for :cmd:`pm buildcache` to
finish and then typing :cmd:`pm collectstatic --noinput`.


Options:

.. option:: --noinput
.. option:: --batch
.. option:: -b

    Do not prompt for user input of any kind.



.. include:: /../docs/shared/include/tested.rst

>>> import lino
>>> lino.startup('lino_book.projects.min1.settings')
>>> from lino.api.doctest import *
>>> from atelier.sheller import Sheller
>>> shell = Sheller(settings.SITE.project_dir)

>>> shell("django-admin buildcache --help")
... #doctest: +NORMALIZE_WHITESPACE +ELLIPSIS +REPORT_UDIFF
usage: django-admin buildcache [-h] [-b] [--version] [-v {0,1,2,3}] [--settings SETTINGS]
                               [--pythonpath PYTHONPATH] [--traceback] [--no-color]
                               [--force-color] [--skip-checks]
<BLANKLINE>
options:
  -h, --help            show this help message and exit
  -b, --batch, --noinput
                        Do not prompt for input of any kind.
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


.. management_command:: buildcache

    This command calls the :meth:`Renderer.build_site_cache
    <lino.core.renderer_mixin.JsCacheRenderer.build_site_cache>` method.
