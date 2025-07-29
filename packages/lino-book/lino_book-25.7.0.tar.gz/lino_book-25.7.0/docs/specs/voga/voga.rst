.. doctest docs/specs/voga/voga.rst
.. _voga.specs.voga:
.. _voga.tested.voga:

====
Voga
====

.. contents::
   :depth: 1
   :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.voga2.startup import *
>>> from django.utils.translation import get_language

>>> print([lng.name for lng in settings.SITE.languages])
['en', 'de', 'fr']


A web request
-------------

The following snippet reproduces a one-day bug on calendar events
whose **time** fields are empty.  Fixed 2013-06-04 in
:func:`lino_xl.lib.cal.utils.when_text`.

>>> print(get_language())
en
>>> client = Client()
>>> d = settings.SITE.demo_date().replace(month=12,day=25)
>>> d = d.strftime(settings.SITE.date_format_strftime)
>>> print(d)
25.12.2015
>>> url = '/api/cal/MyEntries?start=0&limit=16&fmt=json&pv=%s&pv=%s&pv=&pv=&pv=&pv=&pv=&pv=&pv=' % (d,d)
>>> client.force_login(rt.login('robin').user)
>>> res = client.get(url, REMOTE_USER='robin')
>>> print(res.status_code)
200
>>> result = json.loads(res.content.decode())
>>> print(list(sorted(result.keys())))
['count', 'html_text', 'no_data_text', 'overridden_column_headers', 'param_values', 'rows', 'success', 'title']


Printable documents
-------------------

We take a sales invoice, clear the cache, ask Lino to print it and
check whether we get the expected response.

>>> ses = rt.login("robin")
>>> translation.activate('en')
>>> obj = trading.VatProductInvoice.objects.get(journal__ref="SLS", number=11, accounting_period__year__ref='2014')

>>> obj.clear_cache()
>>> obj.printed_by is None
True

>>> obj.clear_cache()
>>> rv = ses.run(obj.do_print)  #doctest: +ELLIPSIS
appy.pod render .../lino_xl/lib/trading/config/trading/VatProductInvoice/Default.odt -> .../media/cache/appypdf/SLS-2014-11.pdf

>>> print(rv['success'])
True
>>> print(rv['open_url'])  #doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
/media/cache/appypdf/SLS-2014-11.pdf
>>> print(rv['message']) #doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
Your printable document (<a href="/media/cache/appypdf/SLS-2014-11.pdf">SLS-2014-11.pdf</a>) should now open in a new browser window. If it doesn't, please ask your system administrator.

Note that we must clear the print cache because leaving the excerpt
there would break a test case in :doc:`db_roger`.

>>> obj.clear_cache()

Same for a calendar Event.  This is mainly to see whether the
templates directory has been inherited.  Note that the first few dozen
events have no `user` and would currently fail to print.

>>> obj = cal.Event.objects.get(pk=100)
>>> obj.clear_cache()
>>> rv = ses.run(obj.do_print) #doctest: +ELLIPSIS
appy.pod render .../lino_xl/lib/cal/config/cal/Event/Default.odt -> .../media/cache/appypdf/cal.Event-100.pdf

>>> print(rv['success'])
True
>>> print(rv['message']) #doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
Your printable document (<a href="/media/cache/appypdf/cal.Event-100.pdf">cal.Event-100.pdf</a>) should now open in a new browser window. If it doesn't, please ask your system administrator.

Note that this test should fail if you run the test suite without a
LibreOffice server running.



>>> show_change_watchers()  #doctest: +NORMALIZE_WHITESPACE +REPORT_UDIFF
================== ============================== ================
 model              master_key                     ignored_fields
------------------ ------------------------------ ----------------
 contacts.Partner   None
 contacts.Company   contacts.Company.partner_ptr
 contacts.Person    contacts.Person.partner_ptr
 courses.Teacher    contacts.Person.partner_ptr
 courses.Pupil      contacts.Person.partner_ptr
================== ============================== ================
<BLANKLINE>

..
  >>> dbhash.check_virgin()
