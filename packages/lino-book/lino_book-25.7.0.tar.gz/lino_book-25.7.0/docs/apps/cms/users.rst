.. doctest docs/plugins/users.rst
.. _cms.plugins.users:

==================================
``users`` in Lino CMS
==================================

The :mod:`lino_cms.lib.users` plugin extends :mod:`lino.modlib.users`.

.. contents::
  :local:

.. include:: /../docs/shared/include/tested.rst

>>> import lino
>>> lino.startup('lino_book.projects.cms1.settings')
>>> from lino.api.doctest import *


Available user types
====================

Lino CMS knows the following :term:`user types <user type>`:

>>> rt.show(rt.models.users.UserTypes)
======= =========== ===============
 value   name        text
------- ----------- ---------------
 000     anonymous   Anonymous
 100     user        User
 800     staff       Staff
 900     admin       Administrator
======= =========== ===============
<BLANKLINE>

A :term:`demo site` has the following users:

>>> rt.show(rt.models.users.UsersOverview)
... #doctest: +NORMALIZE_WHITESPACE +REPORT_UDIFF
========== ===================== ==========
 Username   User type             Language
---------- --------------------- ----------
 andy       100 (User)            en
 bert       100 (User)            en
 chloe      100 (User)            en
 robin      900 (Administrator)   en
 rolf       900 (Administrator)   de
 romain     900 (Administrator)   fr
========== ===================== ==========
<BLANKLINE>


The site manager
================

Robin is a :term:`site manager`, he has a complete menu.

>>> show_menu('robin')
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
- Publisher : Pages, My Blog entries, Sources
- Office : My Upload files, My Comments, Recent comments, Data problem messages assigned to me
- Configure :
  - Publisher : Special pages, Blog Entry Types, Topics, Albums, Licenses, Authors
  - System : Users, Groups, Site contacts, Site configuration, System tasks
  - Office : Library volumes, Upload types, Comment Types
- Explorer :
  - System : Authorities, User types, User roles, Third-party authorizations, Group memberships, Data checkers, Data problem messages, Background procedures, content types
  - Office : Upload files, Upload areas, Comments, Reactions, Mentions
  - Publisher : Blog entries, Tags
- Site : About, User sessions
