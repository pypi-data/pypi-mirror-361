.. doctest docs/plugins/peppol/outbound.rst
.. _dg.plugins.peppol.outbound:

=================================
Outbound Peppol documents
=================================

.. currentmodule:: lino_xl.lib.peppol

.. contents::
  :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.cosi1.startup import *


>>> # pytest.skip('20250619')


The tests in this document are skipped unless you also have :term:`Ibanity
credentials` installed. See :ref:`dg.plugins.peppol.credentials` for details.

>>> if dd.plugins.peppol.credentials is None:
...     pytest.skip('this doctest requires Ibanity credentials')

The test snippets in is document write to the database, that's why we need to
tidy up after a test run. We need to write a customized :func:`tidy_up` function
because :func:`lino.utils.dbhash.check_virgin` can't tidy up every change caused
by running this document.

>>> import shutil
>>> from lino.core.gfks import gfk2lookup
>>> def unused_tidy_up():
...     for obj in peppol.InboundDocument.objects.filter(voucher_id__isnull=False):
...         flt = gfk2lookup(uploads.Upload.owner, obj.voucher)
...         uploads.Upload.objects.filter(**flt).delete()
...         obj.voucher.delete()
...     peppol.InboundDocument.objects.all().delete()
...     shutil.rmtree(dd.plugins.peppol.inbox_dir, ignore_errors=True)
...     peppol.OutboundDocument.objects.all().delete()
...     excerpts.Excerpt.objects.filter(id__gt=6).delete()
...     contacts.Partner.objects.exclude(peppol_id='').update(peppol_id='')
...     accounting.Journal.objects.filter(last_sending__isnull=False).update(last_sending=None)


>>> # tidy_up()

>>> outbound_model = dd.plugins.peppol.outbound_model
>>> ar = rt.login("robin")
>>> ses = dd.plugins.peppol.get_ibanity_session(ar)
>>> translation.activate('en')


>>> ar.show(peppol.Outbox)  #doctest: +NORMALIZE_WHITESPACE +ELLIPSIS




..
  At the end of this page we tidy up the database to avoid side effects in
  other pages:

  >>> dbhash.check_virgin()  #doctest: +ELLIPSIS
  Database ... isn't virgin:
  - excerpts.Excerpt: 4 rows added
  - peppol.OutboundDocument: 5 rows added
  Tidy up 2 rows from database: [(<class 'lino_xl.lib.excerpts.models.Excerpt'>, {...}), (<class 'lino_xl.lib.peppol.documents.OutboundDocument'>, {...})].
  Database has been restored.

  >>> # tidy_up()
