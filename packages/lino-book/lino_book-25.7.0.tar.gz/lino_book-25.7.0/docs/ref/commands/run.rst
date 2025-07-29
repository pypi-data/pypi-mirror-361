.. doctest docs/ref/commands/run.rst

====================================================================
``run`` : run a Python script under the Django environment of a site
====================================================================

.. command:: pm run

For example if you have a file :file:`myscript.py` with the following content in
your project directory...

.. literalinclude:: ../../../lino_book/projects/min1/myscript.py

... then you can run this script using::

    $ pm run myscript.py 101
    Bäckerei Ausdemwald

Saying ``pm run myscript.py`` is almost the same as saying ``manage.py shell <
myscript.py``) (i.e. feeding your script to the stdin of Django's ``shell``
command), but with the possibility of using **command line arguments**.

This command modifies `sys.args`, `__file__` and `__name__` so that
the invoked script sees them as if it had been called directly.

It is similar to the `runscript
<http://django-extensions.readthedocs.org/en/latest/runscript.html>`_
command which comes with `django-extensions
<http://django-extensions.readthedocs.org/en/latest/index.html>`__.

This is yet another answer to the frequently asked Django question
about how to run standalone Django scripts
(`[1] <https://stackoverflow.com/questions/4847469/use-django-from-python-manage-py-shell-to-python-script>`__,
`[2] <http://www.b-list.org/weblog/2007/sep/22/standalone-django-scripts/>`__).


This command is defined by the :mod:`lino` core plugin.


.. include:: /../docs/shared/include/tested.rst

>>> import lino
>>> lino.startup('lino_book.projects.min1.settings')
>>> from lino.api.doctest import *
>>> from atelier.sheller import Sheller
>>> shell = Sheller(settings.SITE.project_dir)

>>> shell("django-admin run --help")  #doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
usage: django-admin run [-h] [--version] [-v {0,1,2,3}] [--settings SETTINGS]
                        [--pythonpath PYTHONPATH] [--traceback] [--no-color] [--force-color]
                        ...
<BLANKLINE>
Run a Python script within the Django environment for this site.
<BLANKLINE>
positional arguments:
  filename              The script to run.
<BLANKLINE>
options:
  -h, --help            show this help message and exit
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

>>> shell("python manage.py run myscript.py 2")  #doctest: +NORMALIZE_WHITESPACE
Bäckerei Ausdemwald
