.. doctest docs/plugins/subscriptions.rst
.. _dg.plugins.subscriptions:

=================================
``subscriptions`` : Subscriptions
=================================

.. currentmodule:: lino_xl.lib.subscriptions

The :mod:`lino_xl.lib.subscriptions` plugin adds functionality for managing
invoice-generating :term:`subscriptions <subscription>`.

For an end-user introduction read :ref:`ug.plugins.subscriptions`.


Table of contents:

.. contents::
   :depth: 1
   :local:


.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.noi1r.startup import *

Dependencies
============

>>> dd.plugins.subscriptions
<lino_xl.lib.subscriptions.Plugin lino_noi.lib.subscriptions(needs ['lino_xl.lib.invoicing'])>

>>> dd.plugins.invoicing
<lino_xl.lib.invoicing.Plugin lino_xl.lib.invoicing(needed by lino_noi.lib.subscriptions, needs ['lino_xl.lib.trading'])>

Examples
========


>>> rt.show(subscriptions.Periodicities)
======= ====== ================ ================
 value   name   Renewal          Renewal before
------- ------ ---------------- ----------------
 w       w      Every 1 weeks    1
 m       m      Every 1 months   7
 q       q      Every 3 months   14
 y       y      Every 1 years    28
======= ====== ================ ================
<BLANKLINE>


>>> rt.show(subscriptions.AllSubscriptions)
==== ================================ ======== ============ =====================
 ID   Journal                          No.      Date         Partner
---- -------------------------------- -------- ------------ ---------------------
 1    Service Level Agreements (SLA)   1        07/01/2014   Rumma & Ko OÜ
 2    Service Level Agreements (SLA)   2        27/01/2014   Bäckerei Ausdemwald
 3    Service Level Agreements (SLA)   3        16/02/2014   Bäckerei Mießen
 4    Service Level Agreements (SLA)   4        08/03/2014   Bäckerei Schmitz
 5    Service Level Agreements (SLA)   5        28/03/2014   Garage Mergelsberg
                                       **15**
==== ================================ ======== ============ =====================
<BLANKLINE>


>>> obj = subscriptions.Subscription.objects.get(pk=2)

>>> rt.show(subscriptions.ItemsBySubscription, obj)
=========================== ========== ============== ========== ========
 Product                     Discount   Unit price     Quantity   Remark
--------------------------- ---------- -------------- ---------- --------
 Hosting (per active user)                             10
 Maintenance                            800,00         1
 Support availability                   700,00         1
 **Total (3 rows)**                     **1 500,00**   **12**
=========================== ========== ============== ========== ========
<BLANKLINE>

The following snippet was added to reproduce #5402 (Replacement index 1 out of
range for positional args tuple):

>>> from lino.core.constants import DISPLAY_MODE_LIST
>>> rt.show(subscriptions.ItemsBySubscription, obj, display_mode=DISPLAY_MODE_LIST)
- ([1](…)) [Hosting (per active user)](…) 10 Pieces
<BLANKLINE>
<BLANKLINE>
- ([2](…)) [Maintenance](…) 1 Pieces à 800.00 €
<BLANKLINE>
<BLANKLINE>
- ([3](…)) [Support availability](…) 1 Pieces à 700.00 €


>>> rt.show(subscriptions.PeriodsBySubscription, obj)
============ ============ ============== ==================== ====
 Start date   End date     Must invoice   Invoicing info       ID
------------ ------------ -------------- -------------------- ----
 27/01/2014   26/01/2015   Yes            `SUB 2/2014 <…>`__   3
 27/01/2015   26/01/2016   Yes            `SUB 2/2015 <…>`__   4
============ ============ ============== ==================== ====
<BLANKLINE>


>>> show_choices('robin', '/choices/tickets/Ticket/order')
... #doctest: +ELLIPSIS
<BLANKLINE>
SLA 1/2014 (welket)
SLA 2/2014 (welsch)
SLA 3/2014 (aab)
SLA 4/2014 (bcc)
SLA 5/2014 (dde)
