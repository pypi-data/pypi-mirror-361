.. doctest docs/specs/ajax.rst
.. _book.specs.ajax:
.. _cosi.tested.bel_de:

===========================================
Refusing permission to an anonymous request
===========================================

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.cosi1.startup import *

This document reproduces a unicode error that occurred when Lino
tried to say "As Anonymous you have no permission to run this action."
in German (where the internationalized text contains non-ascii
characters.

The error was::

  UnicodeEncodeError at /api/trading/InvoicesByJournal
  'ascii' codec can't encode character u'\xfc' in position 64: ordinal not in range(128)


Preliminary tests
=================

This document uses :mod:`lino_book.projects.cosi1`:

>>> print(settings.SETTINGS_MODULE)
lino_book.projects.cosi1.settings

>>> print(settings.SITE.default_user)
None
>>> print(settings.SITE.user_model)
<class 'lino.modlib.users.models.User'>
>>> print(settings.SITE.remote_user_header)
None
>>> print(settings.SITE.get_auth_method())
session
>>> print('\n'.join(settings.MIDDLEWARE))
django.middleware.common.CommonMiddleware
django.middleware.locale.LocaleMiddleware
django.contrib.sessions.middleware.SessionMiddleware
lino.core.auth.middleware.AuthenticationMiddleware
lino.core.auth.middleware.WithUserMiddleware

>>> 'django.contrib.sessions' in settings.INSTALLED_APPS
True

Value of mt and mk in the following snippets must be ...

>>> contenttypes.ContentType.objects.get_for_model(accounting.Journal).id
23
>>> accounting.Journal.objects.get(id=1)
Journal #1 ('Verkaufsrechnungen (SLS)')

Here we go
==========

An end user signs in...

>>> test_client.force_login(rt.login('robin').user)

... and then uses the main menu to open
:class:`lino_xl.lib.trading.InvoicesByJournal`, which will do the following AJAX
call to get its data:

>>> url = '/api/trading/InvoicesByJournal'
>>> url += "?dm=grid&limit=15&fmt=json"
>>> url += "&pv=&pv=&pv=&pv=&pv=&mt=23&mk=1&wt=t"
>>> res = test_client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
>>> # res = test_client.get(url)
>>> res.status_code
200
>>> r = json.loads(res.content.decode())
>>> print(json.dumps(sorted(r.keys())))
["count", "html_text", "no_data_text", "offset", "overridden_column_headers", "param_values", "rows", "success", "title"]
>>> len(r['rows'])
9

It returns only 12 and not 15 rows because :class:`trading.InvoicesByJournal
<lino_xl.lib.trading.InvoicesByJournal>` has :attr:`start_at_bottom
<lino.core.actors.Actor.start_at_bottom>` and because the table contains 72
rows:

>>> trading.InvoicesByJournal.start_at_bottom
True
>>> r['count']
129
>>> r['offset']
120

After seeing this data the user gets a coffee break and leaves their browser
open. The :term:`server administrator` meanwhile does a dump and a reload of the
database. So the sessions have been removed. We simulate this:

>>> x = sessions.Session.objects.all().delete()

The user comes back and resizes their browser window, or some other action that
triggers a refresh.  The browser will issue the same URL, but it will now return
a 403 (Forbidden) response:

>>> import logging
>>> logger = logging.getLogger("django.request")
>>> logger.setLevel(logging.CRITICAL)

>>> res = test_client.get(url)  #doctest: +ELLIPSIS
>>> res.status_code
403
>>> print(res.content.decode().strip())
<!doctype html>
<html lang="en">
<head>
  <title>403 Forbidden</title>
</head>
<body>
  <h1>403 Forbidden</h1><p></p>
</body>
</html>

Lino no longer treats exceptions during an AJAX call specially.

Before 20240921, when an exception like the above occurred during an AJAX call,
Lino's response had a different format, which is defined by the
:mod:`lino.utils.ajax` middleware. Lino recognized AJAX calls by the extra HTTP
header `HTTP_X_REQUESTED_WITH` having the value ``XMLHttpRequest``, which we
must say explicitly to Django's test client.

>>> res = test_client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

Result is now exactly the same as without HTTP_X_REQUESTED_WITH:

>>> res.status_code
403
>>> print(res.content.decode().strip())
<!doctype html>
<html lang="en">
<head>
  <title>403 Forbidden</title>
</head>
<body>
  <h1>403 Forbidden</h1><p></p>
</body>
</html>
