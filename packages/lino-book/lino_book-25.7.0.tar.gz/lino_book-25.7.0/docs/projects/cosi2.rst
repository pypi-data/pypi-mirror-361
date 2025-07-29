.. doctest docs/projects/cosi2.rst

==================================================
``cosi2`` : A Lino Così for Belgium (FR)
==================================================

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.cosi2.startup import *
>>> ses = rt.login('robin')

Used in miscellaneous tested documents, e.g.

- :doc:`/dev/quantities`
- :doc:`/plugins/trading`
- :doc:`/topics/vies`



Miscellaneous
=============

Because :attr:`invoicing` is not installed for cosi2.
:attr:`lino_xl.lib.trading.InvoiceItem.invoiceable` is a dummy field,
which we can see by testing whether :attr:`field` is `None`.

>>> settings.SITE.with_assets
False

>>> print(rt.models.trading.InvoiceItem.invoiceable.field)
None


Slave tables with more than 15 rows
-----------------------------------

When you look at the detail window of Belgium in `Lino Così
<http://demo4.lino-framework.org/api/countries/Countries/BE?an=detail>`_
then you see a list of all places in Belgium.
This demo database contains exactly 48 entries:

>>> be = countries.Country.objects.get(isocode="BE")
>>> be.place_set.count()
48

>>> countries.PlacesByCountry.create_request(be).get_total_count()
48

..
  Value of mt in the following snippets must be ...
  >>> contenttypes.ContentType.objects.get_for_model(countries.Country).id
  5

>>> test_client.force_login(rt.login('robin').user)
>>> url = '/api/countries/PlacesByCountry?fmt=json&start=0&mt=5&mk=BE'
>>> res = test_client.get(url, REMOTE_USER='robin')
>>> print(res.status_code)
200
>>> result = json.loads(res.content.decode('utf-8'))
>>> print(len(result['rows']))
15

The 15 is because Lino has a hard-coded default value of
returning only 15 rows when no limit has been specified.

In versions after :blogref:`20130903` you can change that limit
for a given table by overriding the
:attr:`preview_limit <lino.core.tables.AbstractTable.preview_limit>`
parameter of your table definition.
Or you can change it globally for all your tables
by setting the
:attr:`preview_limit <ad.Site.preview_limit>`
Site attribute to either `None` or some bigger value.

This parameter existed before but wasn't tested.
In your code this would simply look like this::

  class PlacesByCountry(Places):
      preview_limit = 30

Here we override it on the living object:

>>> countries.PlacesByCountry.preview_limit = 25

Same request returns now 25 data rows:

>>> res = test_client.get(url, REMOTE_USER='robin')
>>> result = json.loads(res.content.decode('utf-8'))
>>> print(len(result['rows']))
25

To remove the limit altogether, you can say:

>>> countries.PlacesByCountry.preview_limit = None

and the same request now returns all 49 data rows:

>>> res = test_client.get(url,REMOTE_USER='robin')
>>> result = json.loads(res.content.decode('utf-8'))
>>> print(len(result['rows']))
49

.. _invoices_to_emit:

Invoices to emit
=====================

The cosi2 demo project showcases an approach used e.g. in petrol stations where
customers pay upon delivery when they fill their tank, they want to have a
single invoice at the end of the month where every delivery is mentioned, and
the station is legally required to book their purchases and sales of petrol
every day. Some customers have the privilege of needing to pay only at the end
of the month when they receive the invoice.

Lino helps to manage this kind of situations by using an accounting concept
called `factures à établir
<https://www.compta-online.com/comptabiliser-les-factures-etablir-le-compte-418-ao3071>`__.
The site owner  writes a single daily invoice to a fictive customer "Invoices to
emit". This daily invoice causes VAT to get booked and the daily turnover to
sync with sales and purchases. At the end of the month we then send the actual
invoices to the customers. These invoices don't report about our business
activity, they are only informative, we call them "informal", they list the
deliveries of the last month and just book the total turnover from "Invoices to
emit" to the real customer.

Payment term A means: this is just an informative invoice and the customer has
already paid upon delivery.

>>> obj = trading.VatProductInvoice.objects.filter(payment_term__ref="A").first()
>>> obj
VatProductInvoice #198 ('SLS 9/2023')
>>> rt.show(accounting.MovementsByVoucher, obj)
================== ===== ================= ============ ============ ================ =========
 Account            Car   Partner           Debit        Credit       Match            Cleared
------------------ ----- ----------------- ------------ ------------ ---------------- ---------
 (4000) Customers         Hans Flott & Co   815,96                    **SLS 9/2023**   Yes
 (4000) Customers         Hans Flott & Co                815,96       **SLS 9/2023**   Yes
                                            **815,96**   **815,96**
================== ===== ================= ============ ============ ================ =========
<BLANKLINE>

Payment terms B means: this is just an informative invoice regarding VAT, but
the customer still has to pay.


>>> obj = rt.models.trading.VatProductInvoice.objects.filter(payment_term__ref="B").first()
>>> obj
VatProductInvoice #199 ('SLS 10/2023')
>>> obj.payment_term.informal
True
>>> obj.payment_term.payer
Company #83 ('Invoices to emit')
>>> rt.show(accounting.MovementsByVoucher, obj)
=========================== ===== =========================== ============ ============ ================= =========
 Account                     Car   Partner                     Debit        Credit       Match             Cleared
--------------------------- ----- --------------------------- ------------ ------------ ----------------- ---------
 (4000) Customers                  Bernd Brechts Bücherladen   320,00                    **SLS 10/2023**   No
 (4800) Internal clearings         Invoices to emit                         320,00       **SLS 10/2023**   No
                                                               **320,00**   **320,00**
=========================== ===== =========================== ============ ============ ================= =========
<BLANKLINE>


The customer "Invoices to emit" is used to record internal clearing of invoices
that have been paid at delivery.  TODO: add monthly transaction in the demo
fixture to balance the invoices to emit.


>>> obj = contacts.Company.objects.get(name="Invoices to emit")
>>> obj
Company #83 ('Invoices to emit')
>>> rt.show(accounting.MovementsByPartner, obj, display_mode="grid")
============ ===================== ================================================================================================== ======= ============== ============= =========
 Value date   Voucher               Description                                                                                        Debit   Credit         Match         Cleared
------------ --------------------- -------------------------------------------------------------------------------------------------- ------- -------------- ------------- ---------
 11/02/2025   `SLS 11/2025 <…>`__   `(4800) Internal clearings <…>`__ | `Adriencense Alexine <…>`__ | `Invoices to emit <…>`__                 645,00         SLS 11/2025   No
 14/12/2024   `SLS 57/2024 <…>`__   `(4800) Internal clearings <…>`__ | `Bernd Brechts Bücherladen <…>`__ | `Invoices to emit <…>`__           740,00         SLS 57/2024   No
 10/07/2024   `SLS 29/2024 <…>`__   `(4800) Internal clearings <…>`__ | `Boulanger Abdul Azeez <…>`__ | `Invoices to emit <…>`__               279,90         SLS 29/2024   No
 10/04/2024   `SLS 19/2024 <…>`__   `(4800) Internal clearings <…>`__ | `Booghmans Philomène <…>`__ | `Invoices to emit <…>`__                 320,00         SLS 19/2024   No
 13/02/2024   `SLS 8/2024 <…>`__    `(4800) Internal clearings <…>`__ | `Blondeel Théophile <…>`__ | `Invoices to emit <…>`__                  740,00         SLS 8/2024    No
 07/12/2023   `SLS 54/2023 <…>`__   `(4800) Internal clearings <…>`__ | `Bauwens Isabeau <…>`__ | `Invoices to emit <…>`__                     770,00         SLS 54/2023   No
 07/10/2023   `SLS 43/2023 <…>`__   `(4800) Internal clearings <…>`__ | `Arimont Gaston <…>`__ | `Invoices to emit <…>`__                      600,00         SLS 43/2023   No
 09/07/2023   `SLS 32/2023 <…>`__   `(4800) Internal clearings <…>`__ | `Alloo Béranger <…>`__ | `Invoices to emit <…>`__                      670,00         SLS 32/2023   No
 09/05/2023   `SLS 21/2023 <…>`__   `(4800) Internal clearings <…>`__ | `Adriencense Alexine <…>`__ | `Invoices to emit <…>`__                 990,00         SLS 21/2023   No
 07/03/2023   `SLS 10/2023 <…>`__   `(4800) Internal clearings <…>`__ | `Bernd Brechts Bücherladen <…>`__ | `Invoices to emit <…>`__           320,00         SLS 10/2023   No
                                    **Balance -6074.90 (10 movements)**                                                                        **6 074,90**
============ ===================== ================================================================================================== ======= ============== ============= =========
<BLANKLINE>



Costs by car
============


>>> obj = cars.Car.objects.all().first()
>>> obj
Car #1 ('Alfa Romeo ')
>>> rt.show(accounting.MovementsByProject, obj)
============ ===================== ============================================= ============ ======== ================= =========
 Value date   Voucher               Description                                   Debit        Credit   Match             Cleared
------------ --------------------- --------------------------------------------- ------------ -------- ----------------- ---------
 09/10/2024   `SLS 47/2024 <…>`__   `(4000) Customers <…>`__ / `Bestbank <…>`__   600,00                **SLS 47/2024**   No
                                    **Balance 600.00 (1 movements)**              **600,00**
============ ===================== ============================================= ============ ======== ================= =========
<BLANKLINE>



Explaining the extra cent
==========================

Here is an invoice with quite precise quantities and unit prices, and with
discount amounts. Don't worry about the product name "Wooden table", it doesn't
matter, we just needed a product with 21% VAT rate.

>>> obj = rt.models.trading.VatProductInvoice.objects.filter(journal__ref="SLS").last()
>>> obj
VatProductInvoice #320 ('SLS 16/2025')

>>> print(obj.total_base)
96.85
>>> print(obj.total_vat)
20.34
>>> print(obj.total_incl)
117.19

>>> rt.show(accounting.MovementsByVoucher, obj)
... #doctest: +NORMALIZE_WHITESPACE
================== ===== ============== ============ ============ ================= =========
 Account            Car   Partner        Debit        Credit       Match             Cleared
------------------ ----- -------------- ------------ ------------ ----------------- ---------
 (7000) Sales                                         96,85                          Yes
 (4510) VAT due                                       20,34                          Yes
 (4000) Customers         Adriaen Aimé   117,19                    **SLS 16/2025**   No
                                         **117,19**   **117,19**
================== ===== ============== ============ ============ ================= =========
<BLANKLINE>


>>> rt.show(trading.ItemsByInvoice, obj,
...     column_names="product qty unit_price discount_amount total_incl total_base total_vat ")
... #doctest: +NORMALIZE_WHITESPACE
==================== =========== ======== ========== ============== ============= =============
 Product              Qty         UPr      Discount   TotIncl        TotExcl       VAT
-------------------- ----------- -------- ---------- -------------- ------------- -------------
 Wooden table         30.94       1,5860   2,01       47,0600        38,8926       8,1674
 Wooden table         44.19       1,6520   2,87       70,1300        57,9587       12,1713
 **Total (2 rows)**   **75.13**            **4,88**   **117,1900**   **96,8513**   **20,3387**
==================== =========== ======== ========== ============== ============= =============
<BLANKLINE>


Everything is okay, except that in TIM the same operation results in a total
base of 96.84 instead of 96.85. One cent less. Why? A test in TIM shows that
even TIM would get 96.85 if we manually enter an invoice with these amounts. The
difference comes because the original invoice in TIM had been generated from
delivery notes and using a customized method for computing the discount. So the
VAT amounts in the lines of the invoice differ slightly from what TIM itself
would make them.
This is why tim2lino

::

  Désignation            Qté    p.unit     TVAC       HTVA       MontTVA    V
  ──────────────────────┬──────┬──────────┬──────────┬──────────┬──────────┬──
  Euro Super            │ 30.94│     1.586│     49.07│   40.5544│    8.5164│F
  Rabatt                │  0.00│0         │     -2.01│   -1.6612│   -0.3488│F
  Euro Super            │ 44.19│     1.652│     73.00│   60.3321│   12.6697│F
  Rabatt                │  0.00│0         │     -2.87│   -2.3719│   -0.4981│F
  TOTAL :               │      │          │    117.19│     96.85│   20.3392│
