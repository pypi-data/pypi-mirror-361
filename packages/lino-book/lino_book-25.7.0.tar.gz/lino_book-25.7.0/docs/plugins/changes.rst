.. doctest docs/plugins/changes.rst
.. _dg.plugins.changes:

==================================================
``changes``: Keep track of changes in the database
==================================================

.. currentmodule:: lino.modlib.changes

.. module:: lino.modlib.changes

The :mod:`lino.modlib.changes` plugin adds functionality for recording changes
to individual :term:`database rows <database row>` into a database table.

See :ref:`dev.watch` for an illustrative demo project.

Table of contents:

.. contents::
   :depth: 1
   :local:


What it does
============

The plugin does the following:

- define the :class:`Change` model.
- define the :func:`watch_changes` function
- define a background task ``delete_older_changes``
- add a menu entry :menuselection:`Explorer --> System --> Changes`
- add a `show_changes` button (:guilabel:`≅`) to every watched model


Usage
=====

As the application developer you must explicitly declare which models you want
to watch. You do this in the :meth:`setup_actions
<lino.core.site.Site.setup_actions>` method of your :class:`Site
<lino.core.site.Site>` class. For example here is an excerpt of the
:class:`Site <lino.core.site.Site>` class in :mod:`lino_noi.lib.noi.settings`::

  def setup_actions(self):
      super().setup_actions()
      from lino.modlib.changes.utils import watch_changes as wc
      wc(self.modules.tickets.Ticket, ignore=['_user_cache'])
      wc(self.modules.comments.Comment, master_key='owner')


.. function:: watch_changes(model, ignore=[], master_key=None, **options)

  Declare the specified model to be watched for changes.

  `ignore`, if specified, should be an iterable of field names to be ignored.
  It may be be specified as a string with a space-separated list of field
  names.

  It is allowed to call :func:`watch_changes` multiple times per model.

  Models for which :func:`watch_changes` has been called at least once during
  startup will have their :attr:`Model.change_watcher_spec` set to an instance
  of :class:`WatcherSpec`.




Plugin configuration
====================

.. setting:: changes.remove_after


Database model
==============

.. class:: Change

  Django model to represent a registered change in the database.

  Each database change of a watched object will generate one Change
  record.

  .. attribute:: object

      The database object that has been modified.

  .. attribute:: master

      The database object that acts as "master".



.. class:: Changes

.. class:: ChangesByObject

    Show the history of changes in the current database row.

.. class:: ChangesByMaster

    Show the history of changes in the current database row and related data.


.. class:: ChangeTypes

  The list of possible choices for the `type` field of a :class:`Change`.


Tested code examples
====================


.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.noi1r.startup import *

>>> ses = rt.login("robin")
>>> translation.activate('en')


>>> rt.show(changes.ChangeTypes)
======= ============== ==============
 value   name           text
------- -------------- --------------
 C       create         Create
 U       update         Update
 D       delete         Delete
 R       remove_child   Remove child
 A       add_child      Add child
 M       merge          Merge
======= ============== ==============
<BLANKLINE>


>>> ba = comments.Comments.get_action_by_name('show_changes')
>>> ba.action
<lino.core.actions.ShowSlaveTable show_changes>
>>> print(ba.action.button_text)
≈
>>> print(ba.help_text)
Show the history of changes in the current database row.

>>> ba = tickets.Tickets.get_action_by_name('show_changes')
>>> print(ba.action.button_text)
≅
>>> print(ba.help_text)
Show the history of changes in the current database row and related data.
