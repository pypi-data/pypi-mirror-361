.. doctest docs/projects/cosi5.rst
.. _book.projects.cosi5:

=========================================
``cosi5`` : a Lino Così for Bangladesh
=========================================

.. module:: lino_book.projects.cosi5

A :term:`demo project` showing a :ref:`cosi` configured for usage in Bangladesh.

It is also a proof of concept for a :term:`point of sale`.

See also :doc:`/specs/cosi5/index`.


>>> from lino import startup
>>> startup('lino_book.projects.cosi5.settings')
>>> from lino.api.doctest import *
>>> ses = rt.login('robin')

Overview
========

The :mod:`lino_book.projects.cosi5` demo project is an example of a :ref:`cosi`
having

- the :setting:`accounting.sales_method` set to ``pos`` (:term:`point of sale`)

  >>> dd.plugins.accounting.sales_method
  'pos'

- `Bengali <https://en.wikipedia.org/wiki/Bengali_language>`_ is second language

  >>> [i.django_code for i in settings.SITE.languages]
  ['en', 'bn']


The sales journal
=================

>>> rt.show(accounting.JournalsOverview)
| **SLS** |  0 Sales invoices |
|---------|-------------------|
| **SSN** |  29 Sales notes |
|---------|-----------------|


>>> rt.show('accounting.Journals', column_names="ref name trade_type")
=========== ================ ================== ============
 Reference   Designation      Designation (bn)   Trade type
----------- ---------------- ------------------ ------------
 SLS         Sales invoices   বিক্রয়ের চালান      Sales
 SSN         Sales notes      বিক্রয় চালান        Sales
=========== ================ ================== ============
<BLANKLINE>

>>> rt.show(accounting.PaymentMethods)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE -REPORT_UDIFF
==== ============== ================== ======================== ======
 ID   Designation    Designation (bn)   Payment account          Cash
---- -------------- ------------------ ------------------------ ------
 1    Cash payment   Cash payment       (5700) Cash              Yes
 2    PayPal         PayPal             (5701) Online payments   No
 3    bKash          bKash              (5701) Online payments   No
==== ============== ================== ======================== ======
<BLANKLINE>


>>> jnl = rt.models.accounting.Journal.get_by_ref("SSN")
>>> jnl.voucher_type.table_class
lino_xl.lib.trading.ui.CashInvoicesByJournal

>>> rt.show(jnl.voucher_type.table_class, jnl)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE -REPORT_UDIFF
===================== ============ =================================== =============== ================ =============== =============== ================
 No.                   Date         Partner                             TotIncl         Payment method   Cash received   Cash returned   Workflow
--------------------- ------------ ----------------------------------- --------------- ---------------- --------------- --------------- ----------------
 29/2021               11/06/2021   Evertz Bernd                        2 299,81        PayPal                                           **Registered**
 28/2021               10/06/2021   Ernst Berta                         11,20           Cash payment     15,00           3,80            **Registered**
 27/2021               09/06/2021   Dobbelstein Dorothée                834,00          bKash                                            **Registered**
 26/2021               08/06/2021   Dobbelstein-Demeulenaere Dorothée   580,00          PayPal                                           **Registered**
 25/2021               07/06/2021   Demeulenaere Dorothée               59,85           Cash payment     60,00           0,15            **Registered**
 24/2021               12/05/2021   Dericum Daniel                      2 359,78        bKash                                            **Registered**
 23/2021               11/05/2021   Dericum Daniel                      3 005,45        PayPal                                           **Registered**
 22/2021               10/05/2021   Chantraine Marc                     239,20          Cash payment     240,00          0,80            **Registered**
 21/2021               09/05/2021   Charlier Ulrike                     990,00          bKash                                            **Registered**
 20/2021               08/05/2021   Collard Charlotte                   279,90          PayPal                                           **Registered**
 19/2021               07/05/2021   Bastiaensen Laurent                 1 199,85        Cash payment     1 200,00        0,15            **Registered**
 18/2021               14/04/2021   Ausdemwald Alfons                   3 319,78        bKash                                            **Registered**
 17/2021               13/04/2021   Altenberg Hans                      140,60          PayPal                                           **Registered**
 16/2021               12/04/2021   Arens Annette                       200,00          Cash payment     205,00          5,00            **Registered**
 15/2021               11/04/2021   Arens Annette                       1 045,00        bKash                                            **Registered**
 14/2021               10/04/2021   Arens Andreas                       831,82          PayPal                                           **Registered**
 13/2021               09/04/2021   Auto École Verte                    1 949,85        Cash payment     1 950,00        0,15            **Registered**
 12/2021               08/04/2021   Moulin Rouge                        2 013,88        bKash                                            **Registered**
 11/2021               07/04/2021   Reinhards Baumschule                548,50          PayPal                                           **Registered**
 10/2021               07/03/2021   Bernd Brechts Bücherladen           320,00          Cash payment     325,00          5,00            **Registered**
 9/2021                10/02/2021   Hans Flott & Co                     815,96          bKash                                            **Registered**
 8/2021                09/02/2021   Van Achter NV                       1 939,82        PayPal                                           **Registered**
 7/2021                08/02/2021   Donderweer BV                       1 499,85        Cash payment     1 500,00        0,15            **Registered**
 6/2021                07/02/2021   Garage Mergelsberg                  1 110,16        bKash                                            **Registered**
 5/2021                11/01/2021   Bäckerei Schmitz                    535,00          PayPal                                           **Registered**
 4/2021                10/01/2021   Bäckerei Mießen                     280,00          Cash payment     285,00          5,00            **Registered**
 3/2021                09/01/2021   Bäckerei Ausdemwald                 679,81          bKash                                            **Registered**
 2/2021                08/01/2021   Rumma & Ko OÜ                       2 039,82        PayPal                                           **Registered**
 1/2021                07/01/2021   Miscellaneous                       2 999,85        Cash payment     3 000,00        0,15            **Registered**
 **Total (29 rows)**                                                    **34 128,74**                    **8 780,00**    **20,35**
===================== ============ =================================== =============== ================ =============== =============== ================
<BLANKLINE>

>>> invoice = rt.models.trading.CashInvoice.objects.get(id=1)
>>> print(invoice.payment_method)
Cash payment


>>> rt.show('accounting.MovementsByVoucher', invoice)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE -REPORT_UDIFF
================== =============== ============== ============== ================ =========
 Account            Partner         Debit          Credit         Match            Cleared
------------------ --------------- -------------- -------------- ---------------- ---------
 (7000) Sales                                      2 999,85                        Yes
 (4000) Customers   Miscellaneous   2 999,85                      **SSN 1/2021**   Yes
 (4000) Customers   Miscellaneous                  2 999,85       **SSN 1/2021**   Yes
 (5700) Cash        Miscellaneous   2 999,85                      **SSN 1/2021**   No
                                    **5 999,70**   **5 999,70**
================== =============== ============== ============== ================ =========
<BLANKLINE>

>>> invoice = rt.models.trading.CashInvoice.objects.get(id=2)
>>> print(invoice.payment_method)
PayPal


>>> rt.show('accounting.MovementsByVoucher', invoice)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE -REPORT_UDIFF
======================== =============== ============== ============== ================ =========
 Account                  Partner         Debit          Credit         Match            Cleared
------------------------ --------------- -------------- -------------- ---------------- ---------
 (7000) Sales                                            2 039,82                        Yes
 (4000) Customers         Rumma & Ko OÜ   2 039,82                      **SSN 2/2021**   Yes
 (4000) Customers         Rumma & Ko OÜ                  2 039,82       **SSN 2/2021**   Yes
 (5701) Online payments   Rumma & Ko OÜ   2 039,82                      **SSN 2/2021**   No
                                          **4 079,64**   **4 079,64**
======================== =============== ============== ============== ================ =========
<BLANKLINE>
