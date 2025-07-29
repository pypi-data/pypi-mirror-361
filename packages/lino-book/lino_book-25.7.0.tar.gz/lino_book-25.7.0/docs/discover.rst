.. doctest docs/discover.rst

===========================
Discover some demo projects
===========================

.. contents::
  :local:


More about demo data
====================

The :cmd:`pm prep` command "prepares" the database of a given Lino site. It
flushes the database and loads the **demo fixtures** (see also
:doc:`/dev/demo_fixtures`). Or in other words: **It deletes all data in the
given database and replaces it with "factory default" demo data.**

Of course you don't want this to happen accidentally on a :term:`production
server`. That's why Lino asks::

    INFO Started manage.py prep (using settings)
    We are going to flush your database (.../default.db).
    Are you sure (y/n) ?


Demo projects included with Lino
================================

One of the repositories installed with a Lino :term:`developer environment` is
the :ref:`Lino Book <book>` project, a somewhat special repository:

- It is not an application

- It is not released on PyPI

- It contains the main test suite for Lino.

- It contains the Sphinx source code used to generate the very pages you are
  reading right now (the "Developer Guide").

- It contains a series of :term:`demo projects <demo project>`.

..
  Some of these  demo projects require
  additional Python packages. The easiest way to get them installed all at once is
  to say::

    $ cd ~/lino/env/repositories/book
    $ pip install -r requirements-include.txt

..
  You can now ``cd`` to any subdir of :mod:`lino_book.projects` and run a
  development server.

Let's have a look at one of these demo projects.


The ``polly`` project
=====================

Let's play a bit with the ``polly`` demo project::

  $ go polly
  $ pm prep

Now start a development server::

  $ runserver

Open your browser and discover the **web interface**.

- Please try to create a poll with some questions, then to enter a response to
  that poll.

When you got tired of playing in the web interface, let's discover another
interface: the **command-line**.

.. _pm_shell:

Playing with the Django shell
=============================

Open another terminal and start a **Python shell** on ``polly``::

  $ go polly
  $ pm shell

Now you are almost in a normal Python shell session, with the difference that
your :xfile:`settings.py` has been loaded. Both the `shell
<https://docs.djangoproject.com/en/5.0/ref/django-admin/#shell>`__ and the
`runserver
<https://docs.djangoproject.com/en/5.0/ref/django-admin/#runserver>`__ commands
are part of Django.

Try out whether the following Python commands work also on your computer.

..
  >>> from lino import startup
  >>> startup('lino_book.projects.polly.settings.demo')
  >>> from django.conf import settings

>>> from django.conf import settings

The :mod:`settings` module comes from your :xfile:`settings.py` file.

But don't forget that we are now in the shell, no longer in your text editor.
The Python process is running and Django has imported your :xfile:`settings.py`
file because it was given (in your :xfile:`manage.py`, which was started by
:cmd:`pm`) by the :setting:`DJANGO_SETTINGS_MODULE` environment variable.

>>> import os
>>> os.environ['DJANGO_SETTINGS_MODULE']
'lino_book.projects.polly.settings.demo'

One well-known Django setting is :setting:`INSTALLED_APPS`.

>>> from pprint import pprint
>>> pprint(settings.INSTALLED_APPS)
('lino',
 'lino.modlib.about',
 'lino.modlib.jinja',
 'lino_react.react',
 'lino.modlib.printing',
 'lino.modlib.system',
 'django.contrib.contenttypes',
 'lino.modlib.gfks',
 'lino.modlib.users',
 'lino_xl.lib.xl',
 'lino_xl.lib.polls',
 'django.contrib.staticfiles',
 'django.contrib.sessions')

A Django project becomes a :term:`Lino site` when its :term:`Django settings
module` has a variable named :setting:`SITE` holding an instance of a subclass
of the :class:`lino.core.site.Site` class.

>>> settings.SITE  #doctest: +ELLIPSIS
<lino_book.projects.polly.settings.demo.Site object at ...>

The attributes you gave in your :xfile:`settings.py` file are here:

>>> settings.SITE.default_ui
'lino_react.react'

The ``SITE`` object contains much more information than what you wrote in your
your :xfile:`settings.py` file. For example,
:attr:`settings.SITE.installed_plugins <lino.core.site.Site.installed_plugins>`
is a tuple of the installed plugins:

>>> pprint(settings.SITE.installed_plugins)
(<lino.core.plugin.Plugin lino>,
 <lino.modlib.about.Plugin lino.modlib.about>,
 <lino.modlib.jinja.Plugin lino.modlib.jinja(needed by lino_react.react)>,
 <lino_react.react.Plugin lino_react.react(needs ['lino.modlib.jinja'])>,
 <lino.modlib.printing.Plugin lino.modlib.printing(needed by lino.modlib.system)>,
 <lino.modlib.system.Plugin lino.modlib.system(needed by lino.modlib.gfks, needs ['lino.modlib.printing'])>,
 <lino.core.plugin.Plugin django.contrib.contenttypes(needed by lino.modlib.gfks)>,
 <lino.modlib.gfks.Plugin lino.modlib.gfks(needs ['lino.modlib.system', 'django.contrib.contenttypes'])>,
 <lino.modlib.users.Plugin lino.modlib.users(needs ['lino.modlib.system'])>,
 <lino.core.plugin.Plugin lino_xl.lib.xl(needed by lino_xl.lib.polls)>,
 <lino_xl.lib.polls.Plugin lino_xl.lib.polls(needs ['lino_xl.lib.xl'])>,
 <lino.core.plugin.Plugin django.contrib.staticfiles>,
 <lino.core.plugin.Plugin django.contrib.sessions>)

These things have been put there during :term:`site startup`. If you are
interested in the details, read :doc:`/dev/startup`.

But let's have some more fun!

>>> from lino.api.doctest import *

The :mod:`lino.api.doctest` module contains a collection of utility functions
that are mainly used in :term:`tested documents <tested document>`. But they can
also help you to discover a Lino site.

>>> show_menu("robin")
- Polls : My Polls, My Responses
- Configure :
  - System : Users, Site configuration
  - Polls : Choice Sets
- Explorer :
  - System : content types, Authorities, User types, User roles
  - Polls : Polls, Questions, Choices, Responses, Answer Choices, Answer Remarks
- Site : About, User sessions

The :func:`lino.api.doctest.show_menu` function takes a username as first
mandatory argument and then prints the :term:`application menu`.


Discover more demo projects
===========================

Please play also with the following demo projects in the same way as you played
with ``polly``:

- chatter
- noi1r
- voga1

Where "playing" means for example:

- Try changing the site attribute :setting:`languages` (you need to run
  :cmd:`pm prep` after doing so)

- Change the :setting:`default_ui` site attribute to verify that they work with
  both the ExtJS (``lino.modlib.extjs``, the default value) and the React front
  end (``lino_react.react``). This change does *not* require :cmd:`pm prep`.


Discover some plugins
=====================

Lino comes with a library of plugins. Plugins are modules you can reuse in
applications. Let's discover a few of them now.

Please read the following pages of the Lino User Guide:

- :ref:`ug.plugins.users`
- :ref:`ug.plugins.contacts`
- :ref:`ug.plugins.cal`
- :ref:`ug.plugins.comments`
- :ref:`ug.plugins.courses`
- :ref:`ug.plugins.accounting`

Demo projects and plugins
=============================

The following table shows which demo project uses which plugin:

============ ======= ========= ======= =======
 Plugin       noi1r   chatter   polly   voga1
------------ ------- --------- ------- -------
 users        ☑       ☑         ☑       ☑
 contacts     ☑       □         □       ☑
 cal          ☑       □         □       ☑
 comments     ☑       ☑         □       □
 courses      □       □         □       ☑
 accounting   ☑       □         □       ☑
============ ======= ========= ======= =======


Don't read on
===============

The following code snippet was used to build the projects and plugins table
above, and it *is* used to test whether the information is correct.

>>> from importlib import import_module
>>> import rstgen
>>> rows = []
>>> projects = ["noi1r", "chatter", "polly", "voga1"]
>>> plugins = ("users", "contacts", "cal", "comments", "courses", "accounting")
>>> for pname in plugins:
...     cells = [ pname ]
...     for prjname in projects:
...         settings_module = "lino_book.projects.{}.settings".format(prjname)
...         m = import_module(settings_module)
...         if not hasattr(m, "SITE"):
...             m = import_module(settings_module + ".demo")
...         cells.append("☑" if m.SITE.is_installed(pname) else "□")
...     rows.append(cells)
>>> header = ["Plugin"] + projects
>>> print(rstgen.table(header, rows))
============ ======= ========= ======= =======
 Plugin       noi1r   chatter   polly   voga1
------------ ------- --------- ------- -------
 users        ☑       ☑         ☑       ☑
 contacts     ☑       □         □       ☑
 cal          ☑       □         □       ☑
 comments     ☑       ☑         □       □
 courses      □       □         □       ☑
 accounting   ☑       □         □       ☑
============ ======= ========= ======= =======
<BLANKLINE>
