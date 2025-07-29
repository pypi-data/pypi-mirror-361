.. doctest docs/plugins/finan.rst
.. _xl.specs.finan:
.. _specs.cosi.finan:

==============================
``finan`` : Financial vouchers
==============================

This document describes the :mod:`lino_xl.lib.finan` plugin.
Read :ref:`ug.plugins.finan` before reading this document.

.. contents::
   :depth: 1
   :local:

.. currentmodule:: lino_xl.lib.finan


.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.cosi1.startup import *

>>> ses = rt.login("robin")
>>> translation.activate('en')

This document is based on the following other specifications:

- :ref:`cosi.specs.accounting`
- :ref:`cosi.specs.accounting`

Payment orders
==============

To configure a journal of :term:`payment orders <payment order>`, you set the
following fields:

- :attr:`voucher_type <lino_xl.lib.accounting.Journal.voucher_type>` should be
  "finan.PaymentOrdersByJournal"

- :attr:`partner <lino_xl.lib.accounting.Journal.partner>` ("Organization") should
  point to the bank where you have the account.

- :attr:`dc <lino_xl.lib.accounting.Journal.dc>` (Primary booking direction) should
  be DEBIT because each item should debit (not credit) the partner's account.

- :attr:`account <lino_xl.lib.accounting.Journal.account>` should be your
  :ref:`ug.accounting.CommonAccounts.pending_po` account.

>>> jnl = accounting.Journal.get_by_ref("PMO")
>>> jnl.voucher_type
<accounting.VoucherTypes:finan.PaymentOrdersByJournal>

>>> rt.show("finan.PaymentOrdersByJournal", jnl)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF -SKIP
===================== ============ =========== ================ ================ =================== ================
 No.                   Date         Narration   Total            Execution date   Accounting period   State
--------------------- ------------ ----------- ---------------- ---------------- ------------------- ----------------
 1/2023                13/01/2023               5 619,78                          2023-01             **Registered**
 2/2023                13/02/2023               5 570,39                          2023-02             **Registered**
 3/2023                13/03/2023               5 570,88                          2023-03             **Registered**
 4/2023                13/04/2023               5 571,08                          2023-04             **Registered**
 5/2023                13/05/2023               5 572,28                          2023-05             **Registered**
 6/2023                13/06/2023               5 569,78                          2023-06             **Registered**
 7/2023                13/07/2023               5 670,26                          2023-07             **Registered**
 8/2023                13/08/2023               5 570,88                          2023-08             **Registered**
 9/2023                13/09/2023               5 795,48                          2023-09             **Registered**
 10/2023               13/10/2023               5 572,28                          2023-10             **Registered**
 11/2023               13/11/2023               5 569,78                          2023-11             **Registered**
 12/2023               13/12/2023               6 162,47                          2023-12             **Registered**
 1/2024                13/01/2024               5 626,48                          2024-01             **Registered**
 2/2024                13/02/2024               5 626,68                          2024-02             **Registered**
 3/2024                13/03/2024               5 627,88                          2024-03             **Registered**
 4/2024                13/04/2024               5 625,38                          2024-04             **Registered**
 5/2024                13/05/2024               6 222,51                          2024-05             **Registered**
 6/2024                13/06/2024               5 626,48                          2024-06             **Registered**
 7/2024                13/07/2024               5 741,06                          2024-07             **Registered**
 8/2024                13/08/2024               5 627,88                          2024-08             **Registered**
 9/2024                13/09/2024               5 625,38                          2024-09             **Registered**
 10/2024               13/10/2024               5 625,98                          2024-10             **Registered**
 11/2024               13/11/2024               5 626,48                          2024-11             **Registered**
 12/2024               13/12/2024               5 626,68                          2024-12             **Registered**
 1/2025                13/01/2025               5 683,48                          2025-01             **Registered**
 2/2025                13/02/2025               5 680,98                          2025-02             **Registered**
 **Total (26 rows)**                            **147 408,67**
===================== ============ =========== ================ ================ =================== ================
<BLANKLINE>


.. class:: PaymentOrder

    Django model to represent a :term:`payment order`.

    .. method:: write_xml

      Write the XML file for the SEPA payment initiation from this payment
      order.

    .. attribute:: entry_date

        The date of the ledger entry.

    .. attribute:: execution_date

        The execution date of payment order. If this is empty, Lino
        assumes the :attr:`entry_date` when writing the
        :xfile:`pain_001.xml` file.

    .. attribute:: total

        The total amount. This is automatically computed when you register
        de voucher.


.. class:: PaymentOrderItem

    Django model to represent an individual item of a :term:`payment order`.


.. class:: PaymentOrders

    The base table of all tables on :class:`PaymentOrder`.

.. class:: ItemsByPaymentOrder


Bank statements
===============

>>> rt.show("finan.BankStatementsByJournal", accounting.Journal.get_by_ref("BNK"))
===================== ============ ================ ================ =================== ================
 No.                   Date         Start balance    End balance      Accounting period   State
--------------------- ------------ ---------------- ---------------- ------------------- ----------------
 1/2023                21/01/2023                    2 447,53         2023-01             **Registered**
 2/2023                21/02/2023   2 447,53         1 636,68         2023-02             **Registered**
 3/2023                21/03/2023   1 636,68         -1 851,55        2023-03             **Registered**
 4/2023                21/04/2023   -1 851,55        3 077,73         2023-04             **Registered**
 5/2023                21/05/2023   3 077,73         6 796,23         2023-05             **Registered**
 6/2023                21/06/2023   6 796,23         5 208,52         2023-06             **Registered**
 7/2023                21/07/2023   5 208,52         2 905,93         2023-07             **Registered**
 8/2023                21/08/2023   2 905,93         1 985,21         2023-08             **Registered**
 9/2023                21/09/2023   1 985,21         4 685,00         2023-09             **Registered**
 10/2023               21/10/2023   4 685,00         8 682,96         2023-10             **Registered**
 11/2023               21/11/2023   8 682,96         9 682,87         2023-11             **Registered**
 12/2023               21/12/2023   9 682,87         8 770,14         2023-12             **Registered**
 1/2024                21/01/2024   8 770,14         6 522,63         2024-01             **Registered**
 2/2024                21/02/2024   6 522,63         6 271,24         2024-02             **Registered**
 3/2024                21/03/2024   6 271,24         12 812,17        2024-03             **Registered**
 4/2024                21/04/2024   12 812,17        17 963,80        2024-04             **Registered**
 5/2024                21/05/2024   17 963,80        12 598,23        2024-05             **Registered**
 6/2024                21/06/2024   12 598,23        6 832,45         2024-06             **Registered**
 7/2024                21/07/2024   6 832,45         12 620,19        2024-07             **Registered**
 8/2024                21/08/2024   12 620,19        13 773,55        2024-08             **Registered**
 9/2024                21/09/2024   13 773,55        17 573,93        2024-09             **Registered**
 10/2024               21/10/2024   17 573,93        15 708,26        2024-10             **Registered**
 11/2024               21/11/2024   15 708,26        11 903,70        2024-11             **Registered**
 12/2024               21/12/2024   11 903,70        13 137,18        2024-12             **Registered**
 1/2025                21/01/2025   13 137,18        18 886,04        2025-01             **Registered**
 2/2025                21/02/2025   18 886,04        17 706,43        2025-02             **Registered**
 **Total (26 rows)**                **220 630,62**   **238 337,05**
===================== ============ ================ ================ =================== ================
<BLANKLINE>


.. class:: BankStatement

    Django model to represent a :term:`bank statement`.

    .. attribute:: balance1

        The old (or start) balance.

    .. attribute:: balance2

        The new (or end) balance.

.. class:: BankStatementItem

    Django model to represent an individual item of a :term:`bank statement`.


.. class:: BankStatements

    The base table of all tables on :class:`BankStatement`.


.. class:: ItemsByBankStatement

    Shows the items of a :term:`bank statement`.



Cash journals
=============

>>> rt.show("finan.BankStatementsByJournal", accounting.Journal.get_by_ref("CSH"))
No data to display


Journal entries
===============

>>> rt.show("finan.JournalEntriesByJournal", accounting.Journal.get_by_ref("MSC"))
No data to display

>>> rt.show("finan.JournalEntriesByJournal", accounting.Journal.get_by_ref("PRE"))
======== ============ =========== =================== ================
 No.      Date         Narration   Accounting period   State
-------- ------------ ----------- ------------------- ----------------
 1/2023   01/01/2023               2023-01             **Registered**
======== ============ =========== =================== ================
<BLANKLINE>


.. class:: JournalEntry

    Django model to represent a :term:`journal entry`.

.. class:: JournalEntryItem

    Django model to represent an individual item of a :term:`journal entry`.

.. class:: JournalEntries

    The base table of all tables on :class:`JournalEntry`.

.. class:: ItemsByJournalEntry

    Shows the items of a journal entry.




Model mixins
============

.. class:: FinancialVoucher

    Base class for all :term:`financial vouchers <financial voucher>`.

    .. attribute:: item_account

        The default value to use when
        :attr:`FinancialVoucherItem.account` of an item is empty.

    .. attribute:: item_remark

        The default value to use when
        :attr:`FinancialVoucherItem.remark` of an item is empty.

    .. attribute:: printed
        See :attr:`lino_xl.lib.excerpts.mixins.Certifiable.printed`


.. class:: FinancialVoucherItem

    The base class for the items of all types of financial vouchers
    (:class:`FinancialVoucher`).

    .. attribute:: account

        The general account to be used in the primary booking.
        If this is empty, use :attr:`item_account` of the voucher.

    .. attribute:: project

        The "project" related to this transaction. For example in Lino
        Welfare this is the client.

    .. attribute:: partner

        The partner account to be used in the primary booking.

        In Lino Welfare this field is optional and used only for
        transactions whose *recipient* is different from the *client*.
        When empty, Lino will book to the **client**
        (i.e. :attr:`project`).

    .. attribute:: amount

        The amount to be booked. If this is empty, then the voucher
        cannot be registered.

    .. attribute:: dc

        The direction of the primary booking to create.

    .. attribute:: remark

        External reference. The description of this transation
        as seen by the external partner.

    .. attribute:: seqno

    .. attribute:: match

        An arbitrary string used to group several movements.

        A reference to the voucher that caused this voucher entry.  For
        example the :attr:`match` of the payment of an invoice points
        to that invoice.


In a :term:`bank statement` you might want to specify an individual date for
every item.

.. class:: DatedFinancialVoucher

    A :class:`FinancialVoucher` whose items have a :attr:`date` field.


.. class:: DatedFinancialVoucherItem

    A :class:`FinancialVoucherItem` with an additional :attr:`date`
    field.

    .. attribute:: date

        The value date of this item.


Plugin configuration
====================

.. class:: Plugin

    This :class:`Plugin <lino.core.plugin.Plugin>` class adds some
    entries to the Explorer menu.  It contains the following
    additional attributes:

    .. attribute:: suggest_future_vouchers

        Whether to suggest vouchers whose due_date is in the future.

        The default value is currently `False` because some demo fixtures
        rely on this.  But in most cases this should probably be set to
        `True` because of course a customer can pay an invoice in advance.

        You can specify this for your application::

            def setup_plugins(self):
                self.plugins.finan.suggest_future_vouchers = True
                super(Site, self).setup_plugins()

        Or, as a local system administrator you can also simply set it
        after your :data:`SITE` instantiation::

            SITE = Site(globals())
            ...
            SITE.plugins.finan.suggest_future_vouchers = True


Tables
======

.. class:: FinancialVouchers

    Base class for the default tables of all financial voucher
    types (:class:`JournalEntries` , :class:`PaymentOrders` and
    :class:`BankStatements`).

.. class:: ItemsByVoucher

    The base table of all tables which display the items of a given
    voucher.


Booking suggestions
===================

.. class:: SuggestionsByVoucher

    Shows the suggested items for a given voucher, with a button to
    fill them into the current voucher.

    This is the base class for
    :class:`SuggestionsByJournalEntry`
    :class:`SuggestionsByBankStatement` and
    :class:`SuggestionsByPaymentOrder` who define the class of the
    master_instance (:attr:`master <lino.core.actors.Actor.master>`)

    This is an abstract virtual slave table.

    Every row is a :class:`DueMovement
    <lino_xl.lib.accounting.utils.DueMovement>` object.

.. class:: SuggestionsByJournalEntry

    A :class:`SuggestionsByVoucher` table for a :class:`JournalEntry`.

.. class:: SuggestionsByPaymentOrder

    A :class:`SuggestionsByVoucher` table for a :class:`PaymentOrder`.

.. class:: SuggestionsByBankStatement

    A :class:`SuggestionsByVoucher` table for a :class:`BankStatement`.


.. class:: SuggestionsByVoucherItem

    Displays the payment suggestions for a given voucher *item*, with
    a button to fill them into the current item (creating additional
    items if more than one suggestion was selected).


.. class:: SuggestionsByJournalEntryItem

.. class:: SuggestionsByPaymentOrderItem

    A :class:`SuggestionsByVoucherItem` table for a
    :class:`PaymentOrderItem`.


.. class:: SuggestionsByBankStatementItem

    A :class:`SuggestionsByVoucherItem` table for a
    :class:`BankStatementItem`.


.. class:: ShowSuggestions

    Show suggested items for this voucher.

.. class:: FillSuggestionsToVoucher

    Fill selected suggestions from a SuggestionsByVoucher table into a
    financial voucher.

    This creates one voucher item for each selected row.

.. class:: FillSuggestionsToVoucherItem

    Fill the selected suggestions as items to the voucher. The *first*
    selected suggestion does not create a new item but replaces the
    item for which it was called.


Template files
==============

.. xfile:: pain_001.xml

   Used for writing a SEPA payment initiation.

   :file:`finan/PaymentOrder/pain_001.xml`


.. class:: FinancialVoucherItemChecker
