.. doctest docs/specs/delayed_values.rst
.. _book.topics.delayed_values:

=============================
Delayed values
=============================

This topic guide explains what a :term:`delayed value` is.

.. contents::
  :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.noi1r.startup import *

.. glossary::

  delayed value

    A value of a :term:`store field` that is not computed immediately and for
    which Lino returns a :class:`dict` object that basically just tells
    the client to emit another AJAX request if it wants to know that value.

Lino currently uses a delayed value when rendering the summary of a slave table
of a detail page.

Delayed values are used only when the :term:`front end` supports them, which it
says by setting :attr:`support_async` to True.  Only react has this feature
right now.

>>> settings.SITE.kernel.web_front_ends[0].support_async
True


About the name
==============

A :term:`slave table` can be a valid :term:`data element` of a :term:`detail
layout`, and it is named `foos.Foos` (i.e. with a dot).

>>> # ses = rt.login("robin", renderer=settings.SITE.kernel.default_renderer)
>>> t1 = tickets.Ticket.objects.get(pk=1)
>>> print(t1.order)
SLA 1/2014 (welket)
>>> dv = tickets.AllTickets
>>> ar = dv.create_request(user=rt.login("robin").get_user())
>>> store = dv.get_handle().store
>>> for sf in store.all_fields:
...     if sf is not None:
...         print(sf.name, sf.__class__.__name__, repr(sf.field) )
... #doctest: +REPORT_UDIFF
id AutoStoreField <django.db.models.fields.BigAutoField: id>
summary StoreField <django.db.models.fields.CharField: summary>
group ForeignKeyStoreField <django.db.models.fields.related.ForeignKey: group>
user ForeignKeyStoreField <django.db.models.fields.related.ForeignKey: user>
description StoreField <lino.core.fields.RichTextField: description>
order ForeignKeyStoreField <django.db.models.fields.related.ForeignKey: order>
end_user ForeignKeyStoreField <django.db.models.fields.related.ForeignKey: end_user>
private BooleanStoreField <django.db.models.fields.BooleanField: private>
urgent BooleanStoreField <django.db.models.fields.BooleanField: urgent>
ticket_type ForeignKeyStoreField <django.db.models.fields.related.ForeignKey: ticket_type>
parent ForeignKeyStoreField <django.db.models.fields.related.ForeignKey: parent>
TicketsByParent MethodStoreField <lino.core.fields.HtmlBox: TicketsByParent>
priority IntegerStoreField <django.db.models.fields.IntegerField: priority>
regular_hours StoreField <lino.core.fields.DurationField: regular_hours>
free_hours StoreField <lino.core.fields.DurationField: free_hours>
created DateTimeStoreField <django.db.models.fields.DateTimeField: created>
modified DateTimeStoreField <django.db.models.fields.DateTimeField: modified>
ref StoreField <django.db.models.fields.CharField: ref>
upgrade_notes StoreField <lino.core.fields.RichTextField: upgrade_notes>
state ComboStoreField <lino.core.choicelists.ChoiceListField: state>
assigned_to ForeignKeyStoreField <django.db.models.fields.related.ForeignKey: assigned_to>
planned_time StoreField <lino.core.fields.DurationField: planned_time>
deadline DateStoreField <django.db.models.fields.DateField: deadline>
duplicate_of ForeignKeyStoreField <django.db.models.fields.related.ForeignKey: duplicate_of>
DuplicatesByTicket MethodStoreField <lino.core.fields.HtmlBox: DuplicatesByTicket>
disabled_fields DisabledFieldsStoreField None
disable_editing DisableEditingStoreField None
workflow_buttons VirtStoreField <lino.core.fields.DisplayField>
overview VirtStoreField <lino.core.fields.HtmlBox>
quick_assign_to VirtStoreField <lino.core.fields.DisplayField>
comments.CommentsByRFC VirtStoreField <lino.core.fields.HtmlBox: comments.CommentsByRFC>
uploads.UploadsByController VirtStoreField <lino.core.fields.HtmlBox: uploads.UploadsByController>
tickets.TicketsByParent VirtStoreField <lino.core.fields.HtmlBox: TicketsByParent>
tickets.TicketsByParent VirtStoreField <lino.core.fields.HtmlBox: TicketsByParent>
add_tag VirtStoreField <django.db.models.fields.related.ForeignKey: add_tag>
topics.TagsByOwner VirtStoreField <lino.core.fields.HtmlBox: topics.TagsByOwner>
my_nickname VirtStoreField <django.db.models.fields.CharField: my_nickname>
comments.CommentsByMentioned VirtStoreField <lino.core.fields.HtmlBox: comments.CommentsByMentioned>
working.SessionsByTicket VirtStoreField <lino.core.fields.HtmlBox: working.SessionsByTicket>

>>> d = store.row2dict(ar, t1)
>>> d['tickets.TicketsByParent']
{'delayed_value_url': 'values/tickets/AllTickets/1/tickets.TicketsByParent'}
>>> pprint(d)
... #doctest: +NORMALIZE_WHITESPACE +ELLIPSIS +REPORT_UDIFF
{'DuplicatesByTicket': <Element div at ...>,
 'TicketsByParent': <Element div at ...>,
 'add_tag': None,
 'add_tagHidden': None,
 'assigned_to': None,
 'assigned_toHidden': None,
 'comments.CommentsByMentioned': {'delayed_value_url': 'values/tickets/AllTickets/1/comments.CommentsByMentioned'},
 'comments.CommentsByRFC': {'delayed_value_url': 'values/tickets/AllTickets/1/comments.CommentsByRFC'},
 'created': datetime.datetime(..., tzinfo=datetime.timezone.utc),
 'deadline': None,
 'description': '<p>Screenshot:</p><p>[file 1]</p>',
 'disable_editing': False,
 'disabled_fields': {'DuplicatesByTicket': True,
                     'TicketsByParent': True,
                     'assign_to_me': True,
                     'created': True,
                     'end_session': True,
                     'id': True,
                     'mark_refused': True,
                     'modified': True,
                     'take': True,
                     'wf1': True},
 'duplicate_of': None,
 'duplicate_ofHidden': None,
 'end_user': 'Andreas Arens',
 'end_userHidden': 13,
 'free_hours': None,
 'group': 'Developers',
 'groupHidden': 1,
 'id': 1,
 'modified': datetime.datetime(..., tzinfo=datetime.timezone.utc),
 'my_nickname': None,
 'order': 'SLA 1/2014 (welket)',
 'orderHidden': 1,
 'overview': '<div><h2>Föö fails to bar when baz</h2><p>Screenshot:</p><p><a '
             'href="/#/api/uploads/Uploads/1" target="_blank"><img '
             'src="/media/volumes/screenshots/Screenshot_20250124_104858.png" '
             'style="padding:4px; max-width:100%; max-height:20ex" '
             'title="Screenshot 20250124 104858.png"/></a></p></div>',
 'parent': None,
 'parentHidden': None,
 'planned_time': None,
 'priority': 50,
 'private': False,
 'quick_assign_to': <Element span at ...>,
 'ref': None,
 'regular_hours': None,
 'state': 'New',
 'stateHidden': '10',
 'summary': 'Föö fails to bar when baz',
 'ticket_type': 'Bugfix',
 'ticket_typeHidden': 1,
 'tickets.TicketsByParent': {'delayed_value_url': 'values/tickets/AllTickets/1/tickets.TicketsByParent'},
 'topics.TagsByOwner': {'delayed_value_url': 'values/tickets/AllTickets/1/topics.TagsByOwner'},
 'upgrade_notes': '',
 'uploads.UploadsByController': {'delayed_value_url': 'values/tickets/AllTickets/1/uploads.UploadsByController'},
 'urgent': False,
 'user': 'Jean',
 'userHidden': 7,
 'workflow_buttons': <Element span at ...>,
 'working.SessionsByTicket': {'delayed_value_url': 'values/tickets/AllTickets/1/working.SessionsByTicket'}}

When the client receives data values of type `{'delayed_value_url': ... }`, it
will render the form with those fields empty, emit for each of them an AJAX
request to the specified `delayed_value_url` and fill in the value as soon as it
receives an answer. Here is how such an AJAX request looks like:

>>> url  = "values/tickets/AllTickets/1/working.SessionsByTicket"
>>> demo_get('robin', url, None, -1)
GET /values/tickets/AllTickets/1/working.SessionsByTicket for user Robin Rood got
{'data': '<div class="htmlText"><p>Total 0:00 hours.</p></div>'}




Don't read on
=============

>>> ses = rt.login("robin")
>>> ses.show('tickets.AllTickets.detail', selected_pks=[1])
... #doctest: +NORMALIZE_WHITESPACE +ELLIPSIS +REPORT_UDIFF +SKIP
GeneralMoreLinksFöö fails to bar when bazSubscriptionEnd userTicket typeProjectmarc, rolfPrivatePriorityPlanned timeDeadlineRegularExtraFreeTotal 0:00 hours.[✋] [▶] ⚹ New → [☾] [☎] [☉] [⚒] [☐] [☑]My commentNoneComments of #1 (⚹ Föö fails to bar when baz)BodyCreatedAuthor
WhoWhatDone?HimBar HerFoo the BarxThemFloop the pigx...Rolf Rompenbreaking
<BLANKLINE>
De : lino@foo.net [mailto:foo@bar.com]  Envoyé : mardi 18 octobre 2016 08:52 À : eexample@foo.com Objet : [welcht] YOU modified FOO BAR
 Dear Aurélie ,
this is to notify  / BAR
BAR modified
TODO: include a summary of the modifications.
Any subsequent notifications about foo/  until you view this notification in the Lino web interface. Please visit
None
and follow your welcome messages...JeanIDReferenceSummaryDescription Resolution Source document: NewStateAssigned toAuthorCreatedModifiedFixed sinceDuplicate ofParentChildren of #1 (⚹ Föö fails to bar when baz)PriorityIDSummaryAssign to302Bar is not always baz


More requests to ``/values/``
=============================

Temporary diagnostics after
https://gitlab.com/lino-framework/book/-/jobs/7885272346 regarding the level of
the `django.server <https://docs.djangoproject.com/en/5.0/ref/logging/>`__
logger:

>>> serverlogger = logging.getLogger('django.server')
>>> logging.getLevelName(serverlogger.getEffectiveLevel())
'INFO'
>>> logging.getLevelName(serverlogger.level)
'INFO'


>>> settings.DEBUG = False
>>> test_client.force_login(rt.login('robin').user)

>>> url = "/values/tickets/AllTickets/4694/comments.CommentsByRFC"
>>> res = test_client.get(url)  #doctest: +ELLIPSIS
Ticket matching query does not exist.
Traceback (most recent call last):
...
lino_noi.lib.tickets.models.Ticket.DoesNotExist: Ticket matching query does not exist.
Bad Request: /values/tickets/AllTickets/4694/comments.CommentsByRFC
>>> res.status_code
400
>>> print(res.content.decode()[:9000])
{ "data": "Invalid primary key 4694 for tickets.AllTickets (Ticket matching query does not exist.)" }

>>> settings.SITE.catch_layout_exceptions = True
>>> res = test_client.get(url)  #doctest: +ELLIPSIS
No row 4694 in ActionRequest for ShowTable on tickets.AllTickets
Traceback (most recent call last):
...
lino_noi.lib.tickets.models.Ticket.DoesNotExist: No row 4694 in ActionRequest for ShowTable on tickets.AllTickets
Bad Request: /values/tickets/AllTickets/4694/comments.CommentsByRFC
>>> print(res.content.decode()[:9000])
{ "data": "Invalid primary key 4694 for tickets.AllTickets (No row 4694 in ActionRequest for ShowTable on tickets.AllTickets)" }
>>> settings.SITE.catch_layout_exceptions = False

>>> url = "/values/tickets/AllTickets/112/comments.CommentsByRFC"
>>> res = test_client.get(url)

>>> print(res.status_code)
200

The response to this AJAX request is in JSON:

>>> res.content.decode()  #doctest: +ELLIPSIS
'{ "data": "..." }'

We can parse it into a `dict`:

>>> d = json.loads(res.content.decode())
>>> print(d['data'])  #doctest: +ELLIPSIS
<div class="htmlText">...</div>

>>> url = "/values/tickets/Tickets/112/working.SessionsByTicket"
>>> res = test_client.get(url)
>>> d = json.loads(res.content.decode())
>>> print(d['data'])  #doctest: +ELLIPSIS
<div class="htmlText"><p>...</p></div>

When an incoming request to `/values/` causes some error, this always returns a
JSON error response, never an HTML error report.

>>> url  = "/values/contacts/Persons/5338/contacts.RolesByPerson"
>>> ses = rt.login('robin')
>>> test_client.force_login(ses.user)
>>> settings.DEBUG = True
>>> res = test_client.get(url)
Person matching query does not exist.
Traceback (most recent call last):
...
lino_noi.lib.contacts.models.Person.DoesNotExist: Person matching query does not exist.
Bad Request: /values/contacts/Persons/5338/contacts.RolesByPerson
>>> print(res.status_code)
400
>>> print(res.content.decode())
{ "data": "Invalid primary key 5338 for contacts.Persons (Person matching query does not exist.)" }

This is also true on a production server:

>>> settings.DEBUG = False
>>> res = test_client.get(url)
Person matching query does not exist.
Traceback (most recent call last):
...
lino_noi.lib.contacts.models.Person.DoesNotExist: Person matching query does not exist.
Bad Request: /values/contacts/Persons/5338/contacts.RolesByPerson
>>> print(res.status_code)
400
>>> print(res.content.decode())
{ "data": "Invalid primary key 5338 for contacts.Persons (Person matching query does not exist.)" }

See also :ref:`ticket5763`.
