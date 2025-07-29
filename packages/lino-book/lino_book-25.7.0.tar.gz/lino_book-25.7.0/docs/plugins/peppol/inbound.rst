.. doctest docs/plugins/peppol/inbound.rst
.. _dg.plugins.peppol.inbound:

========================
Inbound Peppol documents
========================

.. currentmodule:: lino_xl.lib.peppol

.. contents::
  :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.cosi2.startup import *

The tests in this document are skipped unless you also have :term:`Ibanity credentials`
installed. See :ref:`dg.plugins.peppol.credentials` for details.

>>> if dd.plugins.peppol.credentials is None:
...     pytest.skip('this doctest requires Ibanity credentials')

..
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
  ...     # peppol.OutboundDocument.objects.all().delete()
  ...     # excerpts.Excerpt.objects.filter(id__gt=6).delete()
  ...     contacts.Partner.objects.exclude(peppol_id='').update(peppol_id='')
  ...     accounting.Journal.objects.filter(last_sending__isnull=False).update(last_sending=None)


  >>> # tidy_up()

>>> ar = rt.login("robin")
>>> ses = dd.plugins.peppol.get_ibanity_session(ar)
>>> translation.activate('en')

>>> rt.show(peppol.Inbox)  #doctest: +NORMALIZE_WHITESPACE +ELLIPSIS

>>> pytest.skip("Inbound docs aren't being tested in the integration environment")

In the beginning our Inbox is empty:

>>> rt.show(peppol.Inbox)  #doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
============================ ============= ============ =============== ================================================================ ===============
 Created at                   Invoice       Partner      Amount          Source document                                                  Voucher state
---------------------------- ------------- ------------ --------------- ---------------------------------------------------------------- ---------------
 2025-06-19 14:39:12.720000   INB 1/2024    Number Two   1 151,70        `⎙ </media/uploads/2025/03/SLS-2024-45.pdf>`__, `⎆ <…>`__, [⏏]   Draft
 2025-06-19 15:27:33.238000   INB 2/2024    Number Two   1 151,70        `⎙ </media/uploads/2025/03/SLS-2024-45.pdf>`__, `⎆ <…>`__, [⏏]   Draft
 2025-06-19 16:25:33.133000   INB 3/2024    Number One   1 151,70        `⎙ </media/uploads/2025/03/SLS-2024-45.pdf>`__, `⎆ <…>`__, [⏏]   Draft
 2025-06-19 16:26:04.295000   INB 4/2024    Number Two   1 151,70        `⎙ </media/uploads/2025/03/SLS-2024-45.pdf>`__, `⎆ <…>`__, [⏏]   Draft
 2025-06-19 19:36:05.646000   INB 5/2024    Number One   1 151,70        `⎙ </media/uploads/2025/03/SLS-2024-45.pdf>`__, `⎆ <…>`__, [⏏]   Draft
 2025-06-19 19:36:35.930000   INB 6/2024    Number Two   1 151,70        `⎙ </media/uploads/2025/03/SLS-2024-45.pdf>`__, `⎆ <…>`__, [⏏]   Draft
 2025-06-19 20:06:18.665000   INB 7/2024    Number One   1 151,70        `⎙ </media/uploads/2025/03/SLS-2024-45.pdf>`__, `⎆ <…>`__, [⏏]   Draft
 2025-06-19 20:55:25.830000   INB 8/2024    Number One   1 151,70        `⎙ </media/uploads/2025/03/SLS-2024-45.pdf>`__, `⎆ <…>`__, [⏏]   Draft
 2025-06-19 20:55:55.924000   INB 9/2024    Number Two   1 151,70        `⎙ </media/uploads/2025/03/SLS-2024-45.pdf>`__, `⎆ <…>`__, [⏏]   Draft
 2025-06-20 01:36:05.097000   INB 10/2024   Number Two   1 151,70        `⎙ </media/uploads/2025/03/SLS-2024-45.pdf>`__, `⎆ <…>`__, [⏏]   Draft
 2025-06-20 01:49:27.181000   INB 11/2024   Number Two   1 151,70        `⎙ </media/uploads/2025/03/SLS-2024-45.pdf>`__, `⎆ <…>`__, [⏏]   Draft
 **Total (11 rows)**                                     **12 668,70**
============================ ============= ============ =============== ================================================================ ===============
<BLANKLINE>


Now Lino can download the detail of every single document.

>>> with ar.print_logger("INFO"):
...     peppol.download_inbound(ses)
... #doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
Download inbound documents
Found 10 inbound documents to download
Created INB 1/2024 from ...
Created INB 2/2024 from ...
Created INB 3/2024 from ...
Created INB 4/2024 from ...
Created INB 5/2024 from ...
Created INB 6/2024 from ...
Created INB 7/2024 from ...
Created INB 8/2024 from ...
Created INB 9/2024 from ...
Created INB 10/2024 from ...

Now the Lino invoice has been created but is not yet registered.

>>> rt.show(peppol.Inbox)  #doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
============================ ============ =============== ============ =============================================================== ===============
 Created at                   Invoice      Partner         Amount       Source document                                                 Voucher state
---------------------------- ------------ --------------- ------------ --------------------------------------------------------------- ---------------
 ...                          INB 1/2014   Rumma & Ko OÜ   822,57       `⎙ </media/uploads/2015/03/SLS-2014-3.pdf>`__, `⎆ <…>`__, [⏏]   Draft
 **Total (1 rows)**                                        **822,57**
============================ ============ =============== ============ =============================================================== ===============
<BLANKLINE>


>>> print(dd.plugins.peppol.inbox_dir)  #doctest: +ELLIPSIS
/.../projects/cosi1/media/ibanity_inbox

>>> for fn in dd.plugins.peppol.inbox_dir.iterdir():
...     print(fn)
/.../projects/cosi1/media/ibanity_inbox/431cb851-5bb2-4526-8149-5655d648292f.xml

..
  Tidy up the database to avoid side effects in other pages:

  >>> dbhash.check_virgin()  #doctest: +ELLIPSIS
  Database ... isn't virgin:
  - excerpts.Excerpt: 4 rows added
  - peppol.OutboundDocument: 5 rows added
  Tidy up 2 rows from database: [(<class 'lino_xl.lib.excerpts.models.Excerpt'>, {...}), (<class 'lino_xl.lib.peppol.documents.OutboundDocument'>, {...})].
  Database has been restored.

  >>> #tidy_up()
