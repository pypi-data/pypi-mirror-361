.. doctest docs/dev/chooser2.rst

.. _book.dev.chooser2:

=====================
More chooser examples
=====================


.. contents::
   :depth: 1
   :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.noi1e.startup import *

Choosers that need the requesting user
======================================

If your chooser method needs to know the current user to determine the choices
for a field, include a "ar" parameter to your chooser method:

.. literalinclude:: /../../book/lino_book/projects/chooser/ar_chooser.py

For example the chooser for the :attr:`lino_xl.lib.tickets.Ticket.group` field
wants to know who is asking before deciding which choices to display, because
not everybody can see every site.

>>> url = '/choices/tickets/Ticket/group'
>>> show_choices("robin", url) #doctest: +ELLIPSIS
<br/>
Developers
Managers
Sales team

>>> show_choices("luc", url) #doctest: +ELLIPSIS
<br/>
Developers
Sales team


Some special cases
==================

Asking choices for a field that doesn't exist:

>>> show_choices("robin", '/choices/tickets/Ticket/foo') #doctest: +ELLIPSIS
Traceback (most recent call last):
...
AttributeError: 'NoneType' object has no attribute 'blank'


Asking choices for a field that exists but has no choices:

>>> show_choices("robin", '/choices/tickets/Ticket/summary') #doctest: +ELLIPSIS
Traceback (most recent call last):
...
Exception: Response status (/choices/tickets/Ticket/summary) was 404 instead of 200

When asking the choices for a field on a slave table, you must specify the
master instance (even though it is not relevant):

>>> url = '/choices/tickets/TicketsByType/group?mk=1'
>>> show_choices("robin", url) #doctest: +ELLIPSIS
<br/>
Developers
Managers
Sales team

When :attr:`lino.core.site.Site.strict_master_check` is True,
**not** specifying a master key when asking the choices for a field on a slave table
is an error:

>>> settings.SITE.strict_master_check = True
>>> url = '/choices/tickets/TicketsByType/group'
>>> show_choices("robin", url) #doctest: +ELLIPSIS
Traceback (most recent call last):
...
Exception: Response status (/choices/tickets/TicketsByType/group) was 400 instead of 200


:class:`lino.modlib.comments.CommentsByRFC` is a :term:`slave table` whose
master field is a GFK. In that case you must also specify the master *type*;
the master *key* is not enough.

>>> comments.CommentsByRFC.master_field  #doctest: +ELLIPSIS
<lino.modlib.gfks.fields.GenericForeignKey: owner>

>>> comments.CommentsByRFC.master_field.name  #doctest: +ELLIPSIS
'owner'

.. preliminary test. Some code snippets in this document use a hard-coded
  mastertype, which might change when plugin odering changes.

  >>> contenttypes.ContentType.objects.get_for_model(tickets.Ticket).pk
  42
  >>> contenttypes.ContentType.objects.get_for_model(comments.Comment).pk
  38

A correct call:

>>> url = '/choices/comments/Comments/owner_id?mk=12&mt=38&owner_type=42&limit=3'
>>> show_choices("robin", url) #doctest: +ELLIPSIS
<br/>
#1 (Föö fails to bar when baz)
#2 (Bar is not always baz)
#3 (Baz sucks)

A call without ``mt`` is allowed because the master type (here Comment) is
known:

>>> show_choices("robin", '/choices/comments/CommentsByRFC/reply_to?mk=12&limit=3')
<br/>
Comment #1
Comment #2
Comment #3


.. /choices/comments/CommentsByRFC/owner_id?limit=15&lv=1708267065.3505688&mk=5440&mt=36&owner_type=36&query=&rp=weak-key-0&start=0

The following snippet was used to reproduce #5440 (Changing the ticket of a
comment doesn't work):

>>> comment = comments.Comment.objects.filter(owner_id=105, owner_type=42).first()
>>> comment
Comment #414 ('Comment #414')

>>> comment.owner
Ticket #105 ('#105 (Irritating message when bar)')
>>> comments.CommentsByRFC.master
<class 'django.contrib.contenttypes.models.ContentType'>

>>> url = '/choices/comments/CommentsByRFC/owner_id?mk=105&mt=42&owner_type=42&limit=3'
>>> show_choices("robin", url) #doctest: +ELLIPSIS
<br/>
#1 (Föö fails to bar when baz)
#2 (Bar is not always baz)
#3 (Baz sucks)
