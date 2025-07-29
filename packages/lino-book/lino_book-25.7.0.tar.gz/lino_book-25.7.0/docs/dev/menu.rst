.. doctest docs/dev/menu.rst
.. _dev.menu:

===============================
More about the application menu
===============================

.. contents::
   :depth: 1
   :local:

Introduction
============

In :ref:`pm_shell` we discovered the :func:`lino.api.doctest.show_menu`
function, which prints the :term:`application menu`.

The :term:`application menu` is an important part of every :term:`Lino
application`. While the :term:`dashboard` shows only the most frequently used
data tables, the application menu gives (or should give) access to every part of
your application.

.. glossary::

  application menu

    The **application menu** or *main menu* specifies how the different
    functionalities of an application are structured when presenting them to a
    :term:`site user`.

Every application has one and only one :term:`application menu`. It's the same
structure for everybody, but users will see only the parts to which they have
access permission. The menu shrinks or expands according to the user's
permissions.

The primitive application menu
==============================

For simple applications you can define the complete menu by overriding the
:meth:`lino.core.site.Site.setup_menu` method of your application.

An example for this approach is in :ref:`dev.polls.settings`.  Let's have a look
at this application.

>>> from lino import startup
>>> startup('lino_book.projects.polls.mysite.settings')

You have seen the application menu in a browser window. But you can also show it
in a documentation page or an interactive Django shell:

>>> from lino.api.doctest import *
>>> show_menu('robin')
- Polls : Questions, Choices
- Site : About

The pluggable application menu
==============================

See :doc:`xlmenu`.
