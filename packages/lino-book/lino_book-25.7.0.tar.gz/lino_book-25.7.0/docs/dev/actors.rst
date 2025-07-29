.. doctest docs/dev/actors.rst
.. _dev.actors:

======================
Introduction to actors
======================

:term:`data tables <data table>` and :term:`choicelists <choicelist>` have certain
things in common. When we refer to them in general, then we call them
:term:`actors <actor>`.

.. contents::
   :depth: 1
   :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino import startup
>>> startup('lino_book.projects.chatter.settings')
>>> from lino.api.doctest import *

Actor types
===========

The most common type of actors are :term:`data tables <data table>`.

But not all actors show tabular data. Another type of actors are *frames*, which
display some data in some other form. One example of a frame actor is the
:menuselection:`Site --> About` dialog window
(:class:`lino.modlib.about.About`). Another example is the :term:`dashboard`
(:class:`lino.modlib.system.Dashboard`). These actors inherit from
:class:`lino.utils.report.EmptyTable`.

The :mod:`lino_xl.lib.calview` plugin uses a complex set of actors.
They all are actually :term:`table actors <table actor>`, but that's not always
visible because they use :term:`display mode` "detail".


.. glossary::

  table actor

    An actor that operates on a list of "rows".

    We happen to simply refer to a table actor as "table", but of course we
    must not mix them up with :term:`database table`.

  database actor

    A :term:`table actor` that is connected to a :term:`database table`.


Identifying actors
==================

Actors are identified by their `app_label.ClassName`. Similar to Django's models
they are globally known unique class objects.

Lino collects actors during :term:`site startup` in a way similar to how Django
collects models.  Every subclass of :class:`lino.core.actors.Actor` that is
defined somewhere in your code, will be "registered" into the global models
namespace :data:`rt.models`.

It makes no difference whether you import them or access them via
:data:`rt.models`. Let's verify this for the `lino_xl.lib.contacts.Persons`
actor:

>>> from lino.modlib.users.models import Users
>>> rt.models.users.Users is Users
True

The advantage of accessing them via :data:`rt.models` is that your code is open
to extensions.

Actors are never instantiated, we use only the class objects.

>>> str(Users)
'users.Users'

>>> repr(Users)
'lino.modlib.users.ui.Users'


Getting a list of all actors
============================

When Lino starts up, it automatically discovers the installed plugins
and registers each subclass of :class:`Actor` as an actor.

>>> len(actors.actors_list)
69

Some of the actors are abstract, i.e. they are used as base classes for other
actors:

>>> len([a for a in actors.actors_list if a.is_abstract()])
14


The actors aren't collected only in this global list but also at different
places depending on their type.

The most common actors are **database tables**. Here we differentiate between
"master tables", "slave tables" and "generic slave tables":

>>> from lino.core import kernel
>>> len(kernel.master_tables)
23

>>> kernel.master_tables[1]
lino.modlib.users.ui.AllUsers

>>> len(kernel.slave_tables)
8
>>> kernel.slave_tables[0]
lino.modlib.users.ui.AuthoritiesGiven


>>> list(sorted(kernel.generic_slaves.values(), key=str))
... #doctest: +NORMALIZE_WHITESPACE
[lino.modlib.comments.ui.CommentsByRFC, lino.modlib.memo.models.MentionsByTarget]


>>> for a in kernel.generic_slaves.values():
...    assert a not in kernel.slave_tables
...    assert a in actors.actors_list


Another category are :term:`virtual tables <virtual table>`.
For example
:class:`lino.modlib.users.UserRoles`
:class:`lino_xl.lib.working.WorkedHours`
:class:`lino.modlib.gfks.BrokenGFKs`
:class:`lino.modlib.gfks.BrokenGFKs`

>>> kernel.virtual_tables  #doctest: +NORMALIZE_WHITESPACE
[lino.modlib.users.ui.UserRoles, lino.modlib.gfks.models.BrokenGFKs,
lino.modlib.gfks.models.BrokenGFKsByModel]


Another category of actors are choicelists

>>> len(kernel.CHOICELISTS)
17
>>> list(sorted(kernel.CHOICELISTS.items()))[6]
('notify.MailModes', lino.modlib.notify.choicelists.MailModes)


Choicelists are stored in both `kernel.CHOICELISTS` and `actors.actors_list`:

>>> for a in kernel.CHOICELISTS.values():
...    if a not in actors.actors_list:
...        print(a)


And a last category are what we call "frames":

>>> kernel.frames_list
[lino.modlib.about.models.About, lino.modlib.system.models.Dashboard]
