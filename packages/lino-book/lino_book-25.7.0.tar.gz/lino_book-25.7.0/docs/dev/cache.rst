===========================
About cached temporary data
===========================

When you run a Lino application, Lino needs a place for storing temporary files
like the SQLite database file, static files and dynamically generated files of
miscellaneous types like `.js`, `.pdf`, `.xls`.

In a normal development environment this is simply below the project directory,
and those cache files are simply listed in the :xfile:`.gitignore` file.

But e.g. on :ref:`travis` it is not allowed to write to the code repository.

In such situations you create an empty directory where you have write
permission, and then set the :envvar:`LINO_CACHE_ROOT` environment variable to
point to it.

The safest place for this directory is below your virtual environment::

  $ cd ~/virtualenvs/a
  $ mkdir lino_cache

And then to add the following line to your :file:`~/virtualenvs/a/bin/activate`
script::

   export LINO_CACHE_ROOT=$VIRTUAL_ENV/lino_cache

Don't forget to re-run the script in order to activate these changes. You can
verify whether the variable is set using this command::

    $ set | grep LINO


.. envvar:: LINO_CACHE_ROOT

If an environment variable :envvar:`LINO_CACHE_ROOT` is set, then the cached
data of a Lino project (e.g. the :xfile:`default.db` files and the
:xfile:`media` directory) are not written into the file tree of the source code
repository but below the given directory.

For example you can add the following line to your :file:`.bashrc` file::

  export LINO_CACHE_ROOT=/home/luc/tmp/cache

Note that the path should be absolute and without a ``~``.


When you use a :envvar:`LINO_CACHE_ROOT` it can happen that the names of your
demo projects clash.  In that case you can manually set a  different
:attr:`project_name <lino.core.site.Site.project_name>`

See also :attr:`lino.core.site.Site.site_dir`.


When to update your static files
================================

(This section is probably obsolete. Don't read.)

.. management_command:: collectstatic

    Lino comes with over 4000 static files, and together they take about 50 MB of
    hard disk storage. To manage them, it uses Django's `staticfiles
    <https://docs.djangoproject.com/en/5.0/ref/contrib/staticfiles/>`_ app, which
    provides the :manage:`collectstatic` command.

    See the `Django documentation
    <https://docs.djangoproject.com/en/5.0/ref/django-admin/#collectstatic>`__

This command is not needed when you use :manage:`runserver`. Only needed on a
:term:`production site`.

Django applications expect static files to be stored in a central
directory pointed to by :setting:`STATIC_ROOT`. And the development
server automatically serves them at the location defined in
:setting:`STATIC_URL`.

:ref:`getlino` automatically sets :setting:`STATIC_ROOT` to a directory named
:file:`collectstatic` under your :envvar:`LINO_CACHE_ROOT`.

As we said in :doc:`hello/index`, before you can see your first Lino application
running in a web server on your machine, you must run Django's
:manage:`collectstatic` command::

    $ python manage.py collectstatic

Theoretically you need to do this only for your first local Lino
project, but you should run :manage:`collectstatic` again:

- after a Lino upgrade
- when you changed your :envvar:`LINO_CACHE_ROOT`
- if you use a plugin with static files for the first time

The following built-in plugins have static files:

- :mod:`lino`
- :mod:`lino.modlib.extjs`
- :mod:`lino.modlib.extensible`
- :mod:`lino.modlib.bootstrap3`
- :mod:`lino.modlib.davlink`
- :mod:`lino.modlib.beid`
- :mod:`lino.modlib.tinymce`

You can run the :manage:`collectstatic` command as often as you want.
So if you are in doubt, just run it again.


Site settings
=============

Some attributes of your :class:`Site <lino.core.site.Site>` instance
which are related to this topic:

.. currentmodule:: lino.core.site

- :attr:`never_build_site_cache <Site.never_build_site_cache>`
- :attr:`build_js_cache_on_startup <Site.build_js_cache_on_startup>`
- :attr:`keep_erroneous_cache_files <Site.keep_erroneous_cache_files>`



Django settings
===============

Some Django settings related to this topic:

.. setting:: STATIC_ROOT

    The root directory where static files are to be collected when the
    `collectstatic` command is run.  See `Django doc
    <https://docs.djangoproject.com/en/5.0/ref/settings/#std:setting-STATIC_ROOT>`__.

    This is not needed as long as you work on a development server
    because the developement server serves static files automagically.

    If this is not set, Lino sets an intelligent default value for it
    as follows.

    When :envvar:`LINO_CACHE_ROOT` is set, the default value for
    :setting:`STATIC_ROOT` is a subdir named :file:`collectstatic` of
    :envvar:`LINO_CACHE_ROOT`.  Otherwise it is set to a subdir named
    :file:`static` of the :attr:`site_dir
    <lino.core.site.Site.site_dir>`.


.. setting:: MEDIA_ROOT

    The root directory of the media files used on this site.  If the
    directory specified by :setting:`MEDIA_ROOT` does not exist, then Lino
    does not create any cache files. Which means that the web interface
    won't work.

    Used e.g. by :mod:`lino.utils.media` :mod:`lino.modlib.extjs` and
    :mod:`lino.mixins.printable`.
