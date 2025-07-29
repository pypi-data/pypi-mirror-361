.. _dev.front_ends:

=====================
More about front ends
=====================

See also :ref:`ug.front_ends` in the :ref:`ug`.

Lino is designed to have *many possible* front ends.  It comes with an
extensible collection of *out-of-the-box* front ends. You can write a Lino
application once and then deploy it via different web interfaces.


The two main web front ends
===========================

There are currently two choices for the front end of a :term:`production site`:

- the legacy :term:`ExtJS front end` is the classical built-in :term:`front end`
  for Lino. It is stable and won't change any more.

- the modern :term:`React front end` has the advantage that your application
  will be usable from a mobile device.

To show the visual difference, here is the ``voga1`` demo project
(a) on the left using the :term:`ExtJS front end` and
(b) on the left using the :term:`React front end`.

.. grid:: 1 1 2 2

  .. grid-item::

    .. image:: frontend1.png
    .. image:: frontend1b.png

  .. grid-item::

    .. image:: frontend2.png
    .. image:: frontend2b.png

You select the front end by setting :setting:`default_ui` in your
:xfile:`settings.py`::

  default_ui = 'lino.modlib.extjs'

  default_ui = 'lino_react.react'

If your :xfile:`settings.py` does not set :setting:`default_ui`, your site will
use the default value, which depends on the application.

.. needed for the next snippet to work
  >>> from lino import startup
  >>> startup('lino_book.projects.voga1.settings')

On the command line you can see this setting by saying::

  $ pm shell
  Python 3.10.12 (main, Jul 29 2024, 16:56:48) [GCC 11.4.0] on linux
  Type "help", "copyright", "credits" or "license" for more information.
  (InteractiveConsole)
  >>> from django.conf import settings
  >>> settings.SITE.default_ui
  'lino.modlib.extjs'
  >>>



Alternative front ends
======================

There are several proofs of concept for alternative front ends.

- The :ref:`extjs6` front end was almost ready for production but went asleep
  because the ExtJS library is unfortunately no longer free. More precisely its
  free community version is not maintained.

- OpenUI5 is developed by SAP, conceptually quite similar to ExtJS.  We
  developed the :mod:`lino_openui5` front end, which was almost ready for
  production, but stopped this project when we discovered :ref:`react`.

  The :ref:`openui5` front end has passed the proof of concept phase, i.e. it is
  visible that it works. But it is not ready for production. There is still much
  work to do. We have no plans to continue this front end because we focus on
  react. But if you are willing to invest your time, then we are glad to support
  you as much as possible.

- The :mod:`lino.modlib.bootstrap3` web interface optimized for read-only access
  and publication of complex data (something like :ref:`belref`). We admit that
  this would need more work before becoming really usable.

- One might consider Lino's :class:`TextRenderer
  <lino.core.renderer.TextRenderer>` (used for writing :doc:`tested
  functional specifications </dev/doctests>`) as a special kind of
  front end.

- a more lightweight web interface using some other JS framework than
  ExtJS.  e.g. `Angular <https://angular.io/>`__ or `Vue
  <https://github.com/vuejs/ui>`__

- A console UI using `ncurses
  <https://en.wikipedia.org/wiki/Ncurses>`_ would be nice.  Not much
  commercial benefit, but a cool tool for system administrators.

- We once started working on an interface that uses the :doc:`Qooxdoo
  library </topics/qooxdoo>`.

- A desktop application using `PyQt
  <https://en.wikipedia.org/wiki/PyQt>`_.
  There is a first prototype of the :manage:`qtclient` command.

- Something similar could be done for `wxWidgets
  <https://en.wikipedia.org/wiki/WxWidgets>`_.

- Support OData to provide an XML or JSON based HTTP interface.


Elements of a front end
=======================

In :doc:`/dev/about/ui` we say that Lino separates business logic and front
end.  That's a noble goal, but the question is *where exactly* you are going to
separate.  The actual challenge is the API between them.

The general elements of every Lino application are:

- the **main menu** : a hierarchical representation of the
  application's functions.  In multi-user applications the main menu
  changes depending on the user's permissions.

- a **grid widget** for rendering tabular data.

- form input using **detail windows** which can contain :ref:`slave
  tables <slave_tables>`, custom panels, ...
