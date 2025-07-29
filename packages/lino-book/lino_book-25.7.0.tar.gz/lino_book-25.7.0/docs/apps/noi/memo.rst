.. doctest docs/apps/noi/memo.rst
.. _noi.specs.memo:

=========================
``memo`` in Noi
=========================

Memo commands in Lino Noi



>>> from lino_book.projects.noi1e.startup import *

The :attr:`description <lino_xl.lib.tickets.Ticket.description>` of a
ticket and the text of a comment (:mod:`short_text
<lino.modlib.comments.Comment.short_text>`) are
:ref:`rich text fields <dev.textfield>`.

And additionally they can contain memo markup commands (see :ref:`dev.memo`).



Lino Noi `memo` command reference
=================================

See also :ref:`memo.builtin`.


.. _memo.ticket:

ticket
======

Refer to a ticket. Usage example:

  See ``[ticket 1]``.

.. _memo.company:

company
=======

Refer to a company. Usage example::

    I met Joe from [company 1] and we agreed...

..
    >>> print(rt.login('robin').parse_memo("See [company 1]."))
    See <a href="…">Rumma &amp; Ko OÜ</a>.

    >>> print(rt.login().parse_memo("See [company 999]."))
    See [ERROR Company matching query does not exist. in '[company 999]' at position 4-17].



.. _memo.person:

person
======

Refer to a person. Usage example::

    I met [person 7 Joe] and we agreed...



>>> from lino.utils.diag import analyzer
>>> print(analyzer.show_memo_commands())
... #doctest: +NORMALIZE_WHITESPACE +REPORT_UDIFF +ELLIPSIS
<BLANKLINE>
- [cal_entry ...] :
  Insert a reference to the specified Calendar entry.
<BLANKLINE>
  The first argument is mandatory and specifies the primary key.
  All remaining arguments are used as the text of the link.
<BLANKLINE>
- [comment ...] :
  Insert a reference to the specified Comment.
<BLANKLINE>
  The first argument is mandatory and specifies the primary key.
  All remaining arguments are used as the text of the link.
<BLANKLINE>
- [company ...] :
  Insert a reference to the specified Organization.
<BLANKLINE>
  The first argument is mandatory and specifies the primary key.
  All remaining arguments are used as the text of the link.
<BLANKLINE>
- [file ...] :
  Insert an image tag of the specified upload file.
<BLANKLINE>
- [group ...] :
  Insert a reference to the specified Team.
<BLANKLINE>
  The first argument is mandatory and specifies the primary key.
  All remaining arguments are used as the text of the link.
<BLANKLINE>
- [person ...] :
  Insert a reference to the specified Person.
<BLANKLINE>
  The first argument is mandatory and specifies the primary key.
  All remaining arguments are used as the text of the link.
<BLANKLINE>
- [product ...] :
  Insert a reference to the specified Product.
<BLANKLINE>
  The first argument is mandatory and specifies the primary key.
  All remaining arguments are used as the text of the link.
<BLANKLINE>
- [ticket ...] :
  Insert a reference to the specified Ticket.
<BLANKLINE>
  The first argument is mandatory and specifies the primary key.
  All remaining arguments are used as the text of the link.
<BLANKLINE>
- [upload ...] :
  Insert a reference to the specified Upload file.
<BLANKLINE>
  The first argument is mandatory and specifies the primary key.
  All remaining arguments are used as the text of the link.
<BLANKLINE>



The ``obj2memo`` method
=======================

Sometimes you want to programmatically generate a text containing memo markup.

For example when your code knows some database object and you want to create a
description that would refer to your object if rendered with memo:

>>> ar = rt.login('robin')
>>> obj = rt.models.tickets.Ticket.objects.get(pk=1)
>>> txt = obj.obj2memo()
>>> print(txt)
[ticket 1] (Föö fails to bar when baz)

Let's also check whether the produced text is valid:

>>> print(ar.parse_memo(txt))
<a href="…" title="Föö fails to bar when baz">#1</a> (Föö fails to bar when baz)


Suggesters
==========

There are two suggesters in :ref:`noi`:  when the user types a "#", they get a
list of tickets. When they type a "@", they get a list with all users.

Every site instance has its global memo parser:

>>> mp = dd.plugins.memo.parser

>>> mp.suggesters.keys()
dict_keys(['@', '#'])

A suggester always returns a maximum of 5 suggestions:

>>> len(list(mp.suggesters['#'].get_suggestions()))
5

Every item of the list is a dict with three keys `value`, `title` and `link`.

>>> pprint(list(mp.suggesters['#'].get_suggestions("12")))
... #doctest: +NORMALIZE_WHITESPACE
[{'link': "javascript:window.App.runAction({'actorId': 'tickets.Tickets', "
          "'action_full_name': 'tickets.Tickets.detail', 'rp': null, 'status': "
          "{'record_id': 12}})",
  'title': '#12 (Foo cannot bar)',
  'value': '12 (Foo cannot bar)'}]

>>> pprint(list(mp.suggesters['#'].get_suggestions("why")))
... #doctest: +NORMALIZE_WHITESPACE +REPORT_UDIFF
[{'link': "javascript:window.App.runAction({'actorId': 'tickets.Tickets', "
          "'action_full_name': 'tickets.Tickets.detail', 'rp': null, 'status': "
          "{'record_id': 20}})",
  'title': '#20 (Why <p> tags are so bar)',
  'value': '20 (Why <p> tags are so bar)'},
 {'link': "javascript:window.App.runAction({'actorId': 'tickets.Tickets', "
          "'action_full_name': 'tickets.Tickets.detail', 'rp': null, 'status': "
          "{'record_id': 32}})",
  'title': '#32 (Why <p> tags are so bar)',
  'value': '32 (Why <p> tags are so bar)'},
 {'link': "javascript:window.App.runAction({'actorId': 'tickets.Tickets', "
          "'action_full_name': 'tickets.Tickets.detail', 'rp': null, 'status': "
          "{'record_id': 44}})",
  'title': '#44 (Why <p> tags are so bar)',
  'value': '44 (Why <p> tags are so bar)'},
 {'link': "javascript:window.App.runAction({'actorId': 'tickets.Tickets', "
          "'action_full_name': 'tickets.Tickets.detail', 'rp': null, 'status': "
          "{'record_id': 56}})",
  'title': '#56 (Why <p> tags are so bar)',
  'value': '56 (Why <p> tags are so bar)'},
 {'link': "javascript:window.App.runAction({'actorId': 'tickets.Tickets', "
          "'action_full_name': 'tickets.Tickets.detail', 'rp': null, 'status': "
          "{'record_id': 68}})",
  'title': '#68 (Why <p> tags are so bar)',
  'value': '68 (Why <p> tags are so bar)'}]


>>> pprint(list(mp.suggesters['@'].get_suggestions()))
... #doctest: +NORMALIZE_WHITESPACE
[{'link': "javascript:window.App.runAction({'actorId': 'users.AllUsers', "
          "'action_full_name': 'users.AllUsers.detail', 'rp': null, 'status': "
          "{'record_id': 7}})",
  'title': 'Jean',
  'value': 'jean'},
 {'link': "javascript:window.App.runAction({'actorId': 'users.AllUsers', "
          "'action_full_name': 'users.AllUsers.detail', 'rp': null, 'status': "
          "{'record_id': 6}})",
  'title': 'Luc',
  'value': 'luc'},
 {'link': "javascript:window.App.runAction({'actorId': 'users.AllUsers', "
          "'action_full_name': 'users.AllUsers.detail', 'rp': null, 'status': "
          "{'record_id': 4}})",
  'title': 'Marc',
  'value': 'marc'},
 {'link': "javascript:window.App.runAction({'actorId': 'users.AllUsers', "
          "'action_full_name': 'users.AllUsers.detail', 'rp': null, 'status': "
          "{'record_id': 5}})",
  'title': 'Mathieu',
  'value': 'mathieu'},
 {'link': "javascript:window.App.runAction({'actorId': 'users.AllUsers', "
          "'action_full_name': 'users.AllUsers.detail', 'rp': null, 'status': "
          "{'record_id': 1}})",
  'title': 'Robin Rood',
  'value': 'robin'}]


>>> pprint(list(mp.suggesters['@'].get_suggestions("ma")))
[{'link': "javascript:window.App.runAction({'actorId': 'users.AllUsers', "
          "'action_full_name': 'users.AllUsers.detail', 'rp': null, 'status': "
          "{'record_id': 4}})",
  'title': 'Marc',
  'value': 'marc'},
 {'link': "javascript:window.App.runAction({'actorId': 'users.AllUsers', "
          "'action_full_name': 'users.AllUsers.detail', 'rp': null, 'status': "
          "{'record_id': 5}})",
  'title': 'Mathieu',
  'value': 'mathieu'},
 {'link': "javascript:window.App.runAction({'actorId': 'users.AllUsers', "
          "'action_full_name': 'users.AllUsers.detail', 'rp': null, 'status': "
          "{'record_id': 3}})",
  'title': 'Romain Raffault',
  'value': 'romain'}]


>>> mp.suggesters['#'].get_object("1")
Ticket #1 ('#1 (Föö fails to bar when baz)')

>>> mp.parse("#1", ar)
'<a href="…" title="#1 (Föö fails to bar when baz)">#1</a>'


Bleaching
=========

Comments are being bleached by default.

Check whether content has been bleached

>>> print(comments.Comment.objects.filter(body="o:OfficeDocumentSettings").first())
None

>> obj  = comments.Comment.objects.filter(body__contains="TODO: include a summary of the modifications.").first()

>>> obj  = comments.Comment.objects.filter(body__contains="and follow your welcome messages").first()
>>> txt = dd.plugins.memo.parser.parse(obj.body)
>>> from lino.utils.soup import truncate_comment
>>> short = truncate_comment(txt)
>>> obj.body_short_preview == short
True
>>> short
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
'breaking  \n \n<strong><span style="font-size: 11.0pt; font-family:
\'Calibri\',\'sans-serif\'; mso-ansi-language: FR;">De\xa0:</span></strong><span
style="font-size: 11.0pt; font-family: \'Calibri\',\'sans-serif\';
mso-ansi-language: FR;"> <a href="mailto:lino@foo.net">lino@foo.net</a> [<a
href="mailto:foo@bar.com">mailto:foo@bar.com</a>] <br/>
<strong>Envoyé\xa0:</strong> mardi 18 octobre 2016 08:52<br/>
<strong>À\xa0:</strong> <a href="mailto:Far@baz.net">eexample@foo.com</a><br/>
<strong>Objet\xa0:</strong> [welcht] YOU modified FOO BAR</span> \n\xa0 \nDear
Aurélie , \nthis is to notify  / BAR \nBAR modified  \nTODO: include a summary
of the modifications. \nAny subsequent notifications about foo/  until you view
this notification in the Lino web interface. Please visit \n<a
href="None">None</a> \nand follow your welcome messages.'

>>> print(obj.body_short_preview)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
breaking
<BLANKLINE>
<strong><span style="font-size: 11.0pt; font-family: 'Calibri','sans-serif'; mso-ansi-language: FR;">De :</span></strong><span style="font-size: 11.0pt; font-family: 'Calibri','sans-serif'; mso-ansi-language: FR;"> <a href="mailto:lino@foo.net">lino@foo.net</a> [<a href="mailto:foo@bar.com">mailto:foo@bar.com</a>] <br/> <strong>Envoyé :</strong> mardi 18 octobre 2016 08:52<br/> <strong>À :</strong> <a href="mailto:Far@baz.net">eexample@foo.com</a><br/> <strong>Objet :</strong> [welcht] YOU modified FOO BAR</span>
 
Dear Aurélie ,
this is to notify  / BAR
BAR modified
TODO: include a summary of the modifications.
Any subsequent notifications about foo/  until you view this notification in the Lino web interface. Please visit
<a href="None">None</a>
and follow your welcome messages.


Above comments were created by the :fixture:`demo2` fixture of
:mod:`lino.modlib.comments`.

.. _permalink_uris:

Permalink URIs
==============

Note that the URI of the link depends on the context.

Of course it depends on the site's front end (specfied in the :attr:`default_ui
<lino.core.site.Site.default_ui>` setting). But when the front end is
:mod:`lino.modlib.extjs`, then we also get a different URL depending on whether
:attr:`lino.core.requests.BaseRequest.permalink_uris` is set or not: Usually we
want a "javascript:..." URI because we don't want the page to reload when
executing an action.

For example when calling it e.g. from :meth:`send_summary_emails
<lino_xl.lib.notify.Message.send_summary_emails>`, we want a "permalink" whose
URI also works in the recipients email client where the JS application isn't yet
loaded. In that case we must explicitly set
:attr:`lino.core.requests.BaseRequest.permalink_uris` to True.

>>> ses = rt.login('robin',
...     renderer=settings.SITE.kernel.default_renderer)

>>> print(ses.parse_memo("See [ticket 1]."))
See <a href="javascript:Lino.tickets.Tickets.detail.run(null,{ &quot;record_id&quot;: 1 })" title="Föö fails to bar when baz" style="text-decoration:none">#1</a>.

>>> ses.permalink_uris = True
>>> print(ses.parse_memo("See [ticket 1]."))
See <a href="/api/tickets/Tickets/1" title="Föö fails to bar when baz" style="text-decoration:none">#1</a>.

While the :mod:`lino.modlib.bootstrap3` front end will render it
like this:

>>> ses = rt.login(renderer=dd.plugins.bootstrap3.renderer)
>>> print(ses.parse_memo("See [ticket 1]."))
See <a href="/bs3/tickets/Tickets/1" title="Föö fails to bar when baz" style="text-decoration:none">#1</a>.

When using this front end, the :attr:`permalink_uris
<lino.core.requests.BaseRequest.permalink_uris>` parameter has no effect:

>>> ses.permalink_uris = True
>>> print(ses.parse_memo("See [ticket 1]."))
See <a href="/bs3/tickets/Tickets/1" title="Föö fails to bar when baz" style="text-decoration:none">#1</a>.

Or the plain text renderer will render:

>>> ses = rt.login()
>>> print(ses.parse_memo("See [ticket 1]."))
See <a href="…" title="Föö fails to bar when baz">#1</a>.
>>> ses.permalink_uris = True
>>> print(ses.parse_memo("See [ticket 1]."))
See <a href="…" title="Föö fails to bar when baz">#1</a>.
