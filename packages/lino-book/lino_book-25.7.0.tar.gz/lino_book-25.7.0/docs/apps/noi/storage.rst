.. doctest docs/apps/noi/storage.rst
.. _noi.plugins.storage:

==================================
``storage`` in Noi
==================================

.. contents::
   :local:
   :depth: 2

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.noi1r.startup import *

Summary
=======

In Noi we have a single :term:`provision state` called "Purchased", which is
used to express purchased credit hours. There is no physical warehouse.


>>> rt.show(storage.ProvisionStates)
... #doctest: +NORMALIZE_WHITESPACE +REPORT_UDIFF
======= =========== ===========
 value   name        text
------- ----------- -----------
 10      purchased   Purchased
======= =========== ===========
<BLANKLINE>

>>> rt.show(storage.Provisions)
... #doctest: +NORMALIZE_WHITESPACE +REPORT_UDIFF
==== ===================== ============= ================= ============
 ID   Partner               Product       Provision state   qty
---- --------------------- ------------- ----------------- ------------
 1    Rumma & Ko OÜ         Hourly rate   Purchased         10:00
 2    Bäckerei Ausdemwald   Hourly rate   Purchased         3:06
 3    Bäckerei Mießen       Hourly rate   Purchased         28:15
 4    Bäckerei Schmitz      Hourly rate   Purchased         90:00
 5    Garage Mergelsberg    Hourly rate   Purchased         10:00
                                                            **141:21**
==== ===================== ============= ================= ============
<BLANKLINE>


>>> rt.show(storage.Fillers)
==== ===================== ================= ================ =============== ============
 ID   Partner               Provision state   Wanted product   Minimum asset   Fill asset
---- --------------------- ----------------- ---------------- --------------- ------------
 1    Rumma & Ko OÜ         Purchased         Hourly rate      2:00            10:00
 2    Bäckerei Ausdemwald   Purchased         Hourly rate      2:00            20:00
 3    Bäckerei Mießen       Purchased         Hourly rate      2:00            50:00
 4    Bäckerei Schmitz      Purchased         Hourly rate      2:00            90:00
 5    Garage Mergelsberg    Purchased         Hourly rate      2:00            10:00
==== ===================== ================= ================ =============== ============
<BLANKLINE>


>>> rt.show(storage.Components)
========================= ============= ===========
 Parent                    Child         qty
------------------------- ------------- -----------
 Hourly rate (emergency)   Hourly rate   1.5
 Time credit (5 hours)     Hourly rate   5:00
 Time credit (10 hours)    Hourly rate   10:00
 Time credit (50 hours)    Hourly rate   50:00
 **Total (4 rows)**                      **66:30**
========================= ============= ===========
<BLANKLINE>


Delivery notes
==============

>>> obj = rt.models.storage.DeliveryNote.objects.filter(partner=1).last()
>>> obj
DeliveryNote #102 ('SRV 14/2015')

>>> obj.partner
Partner #1 ('Rumma & Ko OÜ')

>>> rt.show('storage.ItemsByDeliveryNote', obj)
===================== ================================= ============= =========== ====== =========================================
 No.                   Designation                       Product       Quantity    Move   Invoiced object
--------------------- --------------------------------- ------------- ----------- ------ -----------------------------------------
 1                     03/02/2015 12:53-12:58 Luc #23    Hourly rate   0:05               `03/02/2015 12:53-12:58 Luc #23 <…>`__
 2                     04/02/2015 12:58-15:00 Luc #53    Hourly rate   1:52               `04/02/2015 12:58-15:00 Luc #53 <…>`__
 3                     09/02/2015 09:00-12:53 Luc #83    Hourly rate   3:43               `09/02/2015 09:00-12:53 Luc #83 <…>`__
 4                     10/02/2015 12:48-12:58 Luc #113   Hourly rate   0:10               `10/02/2015 12:48-12:58 Luc #113 <…>`__
 5                     12/02/2015 09:00-10:02 Luc #23    Hourly rate   1:02               `12/02/2015 09:00-10:02 Luc #23 <…>`__
 6                     16/02/2015 09:00-11:18 Luc #53    Hourly rate   2:08               `16/02/2015 09:00-11:18 Luc #53 <…>`__
 7                     17/02/2015 12:29-13:06 Luc #83    Hourly rate   0:37               `17/02/2015 12:29-13:06 Luc #83 <…>`__
 8                     19/02/2015 12:58-13:10 Luc #113   Hourly rate   0:12               `19/02/2015 12:58-13:10 Luc #113 <…>`__
 9                     20/02/2015 12:58-15:00 Luc #23    Hourly rate   1:52               `20/02/2015 12:58-15:00 Luc #23 <…>`__
 10                    25/02/2015 09:00-12:53 Luc #53    Hourly rate   3:43               `25/02/2015 09:00-12:53 Luc #53 <…>`__
 11                    26/02/2015 12:48-12:58 Luc #83    Hourly rate   0:10               `26/02/2015 12:48-12:58 Luc #83 <…>`__
 **Total (11 rows)**                                                   **15:34**
===================== ================================= ============= =========== ====== =========================================
<BLANKLINE>


Don't read this
===============

This section verifies that :ticket:`5704` is done (The MovementsByFiller panel
in FillersByPartner detail doesn't work).

The :class:`MovementsByFiller` slave table is used in at least two different
ways:

- as a slave panel in the detail view of :class:`FillersByPartner`
- as the main widget when shown in its own window

Furthermore it has a customized :meth:`get_master_instance` method: it is
actually just a variant of :class:`MovementsByPartner`.


Values for `mk` and `pk` used in the example:

>>> contenttypes.ContentType.objects.get_for_model(contacts.Company).pk
7
>>> contacts.Company.objects.get(pk=1)
Company #1 ('Rumma & Ko OÜ')

>>> test_client.force_login(rt.login('robin').user)

First request: As a slave panel in the detail view of :class:`FillersByPartner`

>>> url = '/values/storage/FillersByPartner/1/storage.MovementsByFiller'
>>> url += '?mk=1&mt=7'
>>> url += '&rp=weak-key-0'
>>> res = test_client.get(url)  #doctest: +ELLIPSIS

>>> res.status_code
200
>>> rv = json.loads(res.content)
>>> soup = BeautifulSoup(rv['data'], "lxml")
>>> print(soup.get_text())  #doctest: +NORMALIZE_WHITESPACE
SRV 14/2015.1, SLS 8/2015.1, SRV 9/2015.1, SLS 4/2015.1, SRV 4/2015.1, SLS
1/2015.1, SRV 37/2014.1, SLS 22/2014.1, SRV 34/2014.1, SLS 18/2014.1, SRV
28/2014.1, SLS 15/2014.1, SRV 24/2014.1, SLS 12/2014.1, SRV 16/2014.1, ..., ?

>>> links = soup.find_all('a')
>>> len(links)
1

Second request: As the main widget when shown in its own window.

Values for `mk` and `pk` used in the example:

>>> mt = contenttypes.ContentType.objects.get_for_model(storage.Filler).pk
>>> storage.Filler.objects.get(pk=1)
Filler #1 ('Filler Rumma & Ko OÜ Purchased Hourly rate')

>>> url = '/api/storage/MovementsByFiller'
>>> url += '?mk=1&mt={}'.format(mt)
>>> url += '&dm=grid&fmt=json&wt=t'
>>> res = test_client.get(url)  #doctest: +ELLIPSIS
>>> res.status_code
200
>>> rv = json.loads(res.content)
>>> sorted(rv.keys())
['count', 'html_text', 'no_data_text', 'overridden_column_headers', 'param_values', 'rows', 'success', 'title']
>>> len(rv['rows'])
15
>>> rv['title']
'Storage movements of Rumma & Ko OÜ'
