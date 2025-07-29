.. doctest docs/specs/avanti/comments.rst
.. _avanti.specs.comments:

=================================
``comments`` (comments in Avanti)
=================================

.. currentmodule:: lino.modlib.comments

The :mod:`lino.modlib.comments` in :ref:`avanti` is configured and used to
satisfy the application requirements.

.. contents::
  :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.avanti1.startup import *

Overview
========

Comments in :ref:`avanti` are considered confidential data and can be seen only
by users with appropriate permission.

See also :doc:`roles`.

Private comments are seen only by their respective author.

Public comments are shown to other social workers. Comments are never shown to
the *external supervisor*.

A :term:`system administrator` can see *all* comments (it makes no
sense to hide them because a system admin can easily create or use a user
account with the permissions they want).

Comments are private by default:

>>> dd.plugins.comments.private_default
True

All partners are :class:`Commentable`, but in :ref:`avanti`: we use comments
only on :class:`Client`.

>>> list(rt.models_by_base(comments.Commentable))  #doctest: +NORMALIZE_WHITESPACE
[<class 'lino_avanti.lib.avanti.models.Client'>, <class
'lino_xl.lib.contacts.models.Company'>, <class
'lino_xl.lib.contacts.models.Partner'>, <class
'lino_xl.lib.contacts.models.Person'>, <class
'lino_xl.lib.households.models.Household'>, <class
'lino_xl.lib.uploads.models.Upload'>]


Tests
=====

The demo database contains 648 comments, and they are all private.

>>> rt.models.comments.Comment.objects.all().count()
540
>>> rt.models.comments.Comment.objects.filter(private=True).count()
540

Robin can see them all.

>>> rt.login("robin").show(comments.Comments,
...     column_names="id user owner", limit=6,
...     display_mode=DISPLAY_MODE_GRID)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
==== =============== ==================================
 ID   Author          Topic
---- --------------- ----------------------------------
 1    audrey          `BALLO Armáni (80/romain) <…>`__
 2    martina         `BALLO Armáni (80/romain) <…>`__
 3    nathalie        `BALLO Armáni (80/romain) <…>`__
 4    nelly           `BALLO Armáni (80/romain) <…>`__
 5    sandra          `BALLO Armáni (80/romain) <…>`__
 6    Laura Lieblig   `BALLO Armáni (80/romain) <…>`__
==== =============== ==================================
<BLANKLINE>


Nathalie sees only her own comments:

>>> rt.login("nathalie").show(comments.Comments,
...     column_names="id user owner", limit=6, display_mode=DISPLAY_MODE_GRID)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
==== ========== ======================================
 ID   Author     Topic
---- ---------- --------------------------------------
 3    nathalie   `BALLO Armáni (80/romain) <…>`__
 12   nathalie   `ALVANG Aleksándr (79/romain) <…>`__
 21   nathalie   `ABDOO Aátif (78/nathalie) <…>`__
 30   nathalie   `CHAHINE Bánji (75/nelly) <…>`__
 39   nathalie   `BELSKAIA Anton (73/rolf) <…>`__
 48   nathalie   `ABDUL Abbáád (72/romain) <…>`__
==== ========== ======================================
<BLANKLINE>



>>> rt.login("nathalie").show(comments.RecentComments)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
- [... ago](… "Created ...") by **nathalie** in reply to
**martina** about [KEITA Cácey (62/nathalie)](…) : This is a comment about
[Mr Chátá Cisse](/#/api/contacts/Persons/51) and [Mr Chiámáká
Congo](/#/api/contacts/Persons/27).
<BLANKLINE>
...


>>> rt.show(comments.Comments,
...     column_names="id user owner", limit=6)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
<BLANKLINE>


>>> rt.show(comments.RecentComments)
<BLANKLINE>

>>> rt.login("audrey").show(comments.RecentComments)
<BLANKLINE>

Summary:

>>> rows = []
>>> views = (comments.Comments, avanti.Clients)
>>> headers = ["User", "type"] + [i.__name__ for i in views]
>>> user_list = [users.User.get_anonymous_user()] + list(users.User.objects.all())
>>> for u in user_list:
...    cells = [str(u.username), u.user_type.name]
...    for dv in views:
...       qs = dv.create_request(user=u).data_iterator
...       cells.append(str(qs.count()))
...    rows.append(cells)
>>> print(rstgen.table(headers, rows))
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
=========== ============= ========== =========
 User        type          Comments   Clients
----------- ------------- ---------- ---------
 anonymous   anonymous     0          58
 audrey      auditor       0          58
 martina     coordinator   0          58
 nathalie    user          60         58
 nelly       user          60         58
 sandra      secretary     0          58
 laura       teacher       0          58
 romain      admin         540        58
 rolf        admin         540        58
 robin       admin         540        58
=========== ============= ========== =========
<BLANKLINE>
