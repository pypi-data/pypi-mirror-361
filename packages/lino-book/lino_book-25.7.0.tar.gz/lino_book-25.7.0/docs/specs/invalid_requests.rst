.. doctest docs/specs/invalid_requests.rst
.. _invalid_requests:
.. _lino.specs.invalid_requests:

=============================
Answering to invalid requests
=============================

.. contents::
  :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.cosi1.startup import *

>>> settings.SITE.kernel.web_front_ends
[<lino_react.react.Plugin lino_react.react(needs ['lino.modlib.jinja'])>]


403 PermissionDenied
====================

The following request caused a traceback
:message:`type object 'AnonymousUser' has no attribute 'get_chooser_for_field'`
rather than responding PermissionDenied:

>>> url = '/api/users/Me/2?dm=detail&fmt=json&ul=en&wt=d'
>>> res = test_client.get(url)  #doctest: +ELLIPSIS
Forbidden (Permission denied): /api/users/Me/2
Traceback (most recent call last):
...
django.core.exceptions.PermissionDenied: anonymous has no permission to run ActionRequest for ShowDetail on users.Me

>>> res.status_code
403

Lino currently returns HTML content even though ``fmt=json`` has been requested:

>>> print(res.content.decode())
<BLANKLINE>
<!doctype html>
<html lang="en">
<head>
  <title>403 Forbidden</title>
</head>
<body>
  <h1>403 Forbidden</h1><p></p>
</body>
</html>
<BLANKLINE>

TODO: return JSON content rather than HTML



400 Bad Request
===============

A status code of 400 (Bad Request) means "The request could not be understood by
the server due to malformed syntax. The client SHOULD NOT repeat the request
without modifications." (`w3.org
<https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10>`__)

We are going to send some requests to :class:`contacts.RolesByPerson
<lino_xl.lib.contacts.RolesByPerson>`, a slave table on person. So we need a
person as master instance:

>>> contacts.Person.objects.get(pk=15)
Person #15 ('Mrs Annette Arens')

>>> contacts.RolesByPerson.master
<class 'lino_xl.lib.contacts.models.Person'>

Value of ``mt`` ("master type") in the following snippets must be 8:

>>> contenttypes.ContentType.objects.get_for_model(contacts.Person).id
8

We are authenticated as ``robin``:

>>> test_client.force_login(rt.login('robin').user)

Here is a valid request to :class:`contacts.RolesByPerson`:

>>> url = "/api/contacts/RolesByPerson?fmt=json&start=0&limit=15&mt=8&mk=15"
>>> res = test_client.get(url)
>>> print(res.status_code)
200
>>> d = AttrDict(json.loads(res.content.decode()))
>>> d.count
2
>>> print(d.title)
Mrs Annette Arens is contact person for


The examples below explore what happens when a request specifies an *invalid
primary key* for the master (114114 instead of 15).

>>> url = "/api/contacts/RolesByPerson?fmt=json&start=0&limit=15&mt=8&mk=114114"

Lino's default behaviour is to return an empty list of rows and a title
indicating the problem:

>>> res = test_client.get(url)  #doctest: +ELLIPSIS
20240731 MissingRow('Person matching query does not exist. (pk=114114)') is not a <class 'lino_xl.lib.contacts.models.Person'> (contacts.RolesByPerson.master_key = 'person')
>>> res.status_code
200
>>> print(res.content.decode())  #doctest: +NORMALIZE_WHITESPACE
{ "count": 0, "html_text": null, "no_data_text": "No data to display", "overridden_column_headers": {
 }, "rows": [  ], "success": true, "title": "MissingRow(Person matching query does not exist. (pk=114114)) is contact person for" }

Another behaviour is when :attr:`lino.core.site.Site.strict_master_check` is set
to True.  Django will internally raise an :class:`ObjectDoesNotExist` exception,
but Lino catches this and raises a :class:`BadRequest` instead, for which has
some out of the box handling:

>>> settings.SITE.strict_master_check = True
>>> res = test_client.get(url)  #doctest: +ELLIPSIS
MissingRow(Person matching query does not exist. (pk=114114)): /api/contacts/RolesByPerson
Traceback (most recent call last):
...
django.core.exceptions.BadRequest: MissingRow(Person matching query does not exist. (pk=114114))


Django handles :class:`BadRequest` exceptions automatically.
They usually just get logged, and the response gets a 400 status code.
Or when you set the logging level to CRITICAL, they won't even get logged.

>>> import logging
>>> logger = logging.getLogger("django.request")
>>> logger.setLevel(logging.CRITICAL)
>>> settings.DEBUG = False
>>> url = "/api/contacts/RolesByPerson?fmt=json&start=0&limit=15&mt=8&mk=foo"
>>> res = test_client.get(url)  #doctest: +ELLIPSIS

>>> res.status_code
400
>>> print(res.content.decode())
<BLANKLINE>
<!doctype html>
<html lang="en">
<head>
  <title>Bad Request (400)</title>
</head>
<body>
  <h1>Bad Request (400)</h1><p></p>
</body>
</html>
<BLANKLINE>

>>> logger.setLevel(logging.INFO)

Most slave tables have a known :attr:`Actor.master`, which is given by the
target of the :attr:`master_key` field. For example, `RolesByPerson` has
`contacts.Person` as master.

>>> contacts.RolesByPerson.master
<class 'lino_xl.lib.contacts.models.Person'>

So the ``mt`` url parameter is  notrequired. But *if* it is specified, it
overrides the default value, and an invalid value for ``mt`` raises an
exception:

>>> url = "/api/contacts/RolesByPerson?fmt=json&start=0&limit=15&mt=8888&mk=15"
>>> res = test_client.get(url)  #doctest: +ELLIPSIS
Invalid master_type 8888: /api/contacts/RolesByPerson
Traceback (most recent call last):
...
django.core.exceptions.BadRequest: Invalid master_type 8888

>>> res.status_code
400

Request data not supplied
=========================

After 20170410 the following AJAX request no longer raises a real exception but
continues to log it. Raising an exception had the disadvantage of having an
email sent to the :setting:`ADMINS`, which was just disturbing and not helpful
because it had no "request data supplied". Now the :term:`end user` gets an
appropriate message because it receives a status code 400.

>>> url = '/api/cal/EventsByProject?_dc=1491615952104&fmt=json&rp=ext-comp-1306&start=0&limit=15&mt=13&mk=188'
>>> res = test_client.get(url)  #doctest: +ELLIPSIS
Not Found: /api/cal/EventsByProject

>>> res.status_code
404
>>> #print(json.loads(res.content)['message'])
>>> print(res.content.decode())
<BLANKLINE>
<!doctype html>
<html lang="en">
<head>
  <title>Not Found</title>
</head>
<body>
  <h1>Not Found</h1><p>The requested resource was not found on this server.</p>
</body>
</html>
<BLANKLINE>


ValueError: Field 'id' expected a number but got '\ufeff'
=========================================================

The following URL with a ticket number starting with a `BOM
<https://en.wikipedia.org/wiki/Byte_order_mark>`__ (it had been manually pasted
from somewhere else) caused a traceback on Jane but seems to react normally on a
development server.

>>> url = '/api/tickets/AllTickets/%EF%BB%BF'
>>> res = test_client.get(url)  #doctest: +ELLIPSIS
Not Found: /api/tickets/AllTickets/﻿
>>> res.status_code
404
