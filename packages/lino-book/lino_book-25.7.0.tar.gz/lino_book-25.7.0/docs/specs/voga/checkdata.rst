.. doctest docs/specs/voga/checkdata.rst
.. _voga.specs.checkdata:

=======================================
``checkdata`` in Lino Voga
=======================================

Lino Voga uses the :ref:`checkdata <book.specs.checkdata>` plugin for managing
data problem messages.


.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.voga2.startup import *


Data checkers available in Lino Voga
====================================

In the web interface you can select :menuselection:`Explorer -->
System --> Data checkers` to see a table of all available
checkers.

>>> show_menu_path(checkdata.Checkers)
Explorer --> System --> Data checkers

>>> rt.show(checkdata.Checkers)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
=================================== ========================================================
 value                               text
----------------------------------- --------------------------------------------------------
 accounting.VoucherChecker           Check integrity of numbered vouchers
 beid.SSINChecker                    Check for invalid SSINs
 cal.ConflictingEventsChecker        Check for conflicting calendar entries
 cal.EventGuestChecker               Entries without participants
 cal.LongEntryChecker                Too long-lasting calendar entries
 cal.ObsoleteEventTypeChecker        Obsolete generated calendar entries
 countries.PlaceChecker              Check data of geographical places
 courses.MemberChecker               Check membership payments
 finan.FinancialVoucherItemChecker   Check for invalid account/partner combination
 memo.PreviewableChecker             Check for previewables needing update
 phones.ContactDetailsOwnerChecker   Check for mismatches between contact details and owner
 printing.CachedPrintableChecker     Check for missing target files
 sepa.BankAccountChecker             Check for partner mismatches in bank accounts
 system.BleachChecker                Find unbleached html content
 uploads.UploadChecker               Check metadata of upload files
 uploads.UploadsFolderChecker        Find orphaned files in uploads folder
 vat.VatColumnsChecker               Check VAT columns configuration
 vat.VatIdChecker                    Validate VAT id from online registry
=================================== ========================================================
<BLANKLINE>

More information about each checker in the corresponding plugin specs  (e.g.
:class:`beid.SSINChecker <lino_xl.lib.beid.SSINChecker>` is defined in
:mod:`lino_xl.lib.beid` and hence documented in :doc:`/specs/beid`)


..
  >>> dbhash.check_virgin()
