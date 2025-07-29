.. doctest docs/topics/get_change_body.rst

==================================
The :meth:`get_change_body` method
==================================

This document tests the :meth:`get_change_body
<lino.modlib.notify.ChangeNotifier.get_change_body>` method of the
:class:`lino.modlib.notify.ChangeNotifier` mixin.

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.noi1r.startup import *

>>> from lino.core.diff import ChangeWatcher
>>> from lino.modlib.notify.mixins import ChangeNotifier

Here are the change notifiers used in Lino Noi:

>>> pprint(rt.models_by_base(ChangeNotifier))
[<class 'lino_noi.lib.cal.models.Event'>,
 <class 'lino_xl.lib.cal.models.Task'>,
 <class 'lino.modlib.comments.models.Comment'>,
 <class 'lino_noi.lib.groups.models.Group'>,
 <class 'lino_noi.lib.tickets.models.Ticket'>]


>>> obj = tickets.Ticket.objects.first()
>>> cw = None
>>> cw = ChangeWatcher(obj)
>>> ar = rt.login("robin", renderer=settings.SITE.kernel.default_renderer, permalink_uris=True)
>>> obj.summary = "foo"

Just to verify that our change watcher works:

>>> cw.is_dirty()
True
>>> from etgen.html import tostring
>>> tostring(cw.get_updates_html())
'<li><b>Summary</b> : Föö fails to bar when baz --&gt; foo</li>'

The reason for #5038 (Links in email notifications are escaped) on 2023-08-22
was that  the ``<a href ...>`` in the text returned by :meth:`get_change_body`
was getting escaped. This is fixed now:

>>> obj.get_change_body(ar, cw)
'<div><p>Robin Rood modified <a href="/#/api/tickets/Tickets/1" style="text-decoration:none">#1 (foo)</a>:</p><ul><li><b>Summary</b> : Föö fails to bar when baz --&gt; foo</li></ul></div>'


Let's repeat this for other database objects in order to increase test coverage!

>>> def test(obj, **kwargs):
...     cw = ChangeWatcher(obj)
...     print(obj.get_change_body(ar, None))
...     for k, v in kwargs.items():
...         setattr(obj, k, v)
...     print(obj.get_change_body(ar, cw))

>>> test(cal.Event.objects.first(), start_time=datetime.time(10,5))
<div><p>Robin Rood created <a href="/#/api/cal/Events/1" style="text-decoration:none">New Year's Day (01.01.2013)</a></p>.</div>
<div><p>Robin Rood modified <a href="/#/api/cal/Events/1" style="text-decoration:none">New Year's Day (01.01.2013 10:05)</a>:</p><ul><li><b>Start time</b> : None --&gt; 10:05:00</li></ul></div>

The :class:`lino.modlib.comments.Comment` model has a customized change body:

>>> test(comments.Comment.objects.first(), body="Foo")
... #doctest: +NORMALIZE_WHITESPACE
Robin Rood commented on <a href="/#/api/contacts/Companies/95" style="text-decoration:none">Number Three</a>:<br><p>Here is a screenshot:
<BLANKLINE>
 [file 1]</p>
Robin Rood modified comment on <a href="/#/api/contacts/Companies/95" style="text-decoration:none">Number Three</a>:<br>Foo
