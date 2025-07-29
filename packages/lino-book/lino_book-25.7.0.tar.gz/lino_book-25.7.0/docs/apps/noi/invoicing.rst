.. doctest docs/apps/noi/invoicing.rst
.. _noi.specs.invoicing:

======================================
``invoicing`` in Noi
======================================


.. contents::
  :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.noi1r.startup import *


Overview
========

A **subscription** generates one invoice per year or month. Each invoice for a
same customer has the same amount. :term:`Working sessions <working session>`
generate :term:`service reports <service report>`, which are just internal
delivery notes, not invoices. **Fillers** monitor the time credit of customers
and generate an invoice to buy new credit when needed. And the first invoice
generator, :class:`lino_xl.lib.trading.InvoiceItem`, is not used.


>>> rt.show(accounting.JournalsOverview)
| **SLS** |  39 Sales invoices |
|---------|--------------------|
| **SUB** |  11 Subscription invoices |
|---------|---------------------------|
| **SRV** |  55 Service reports |
|---------|---------------------|
| **SLA** |  5 Service Level Agreements |
|---------|-----------------------------|



>>> rt.show('invoicing.Tasks')
... #doctest: +NORMALIZE_WHITESPACE +REPORT_UDIFF +ELLIPSIS
===== ================================== ========== =========== =========================...===
 No.   Name                               Disabled   When        Status
----- ---------------------------------- ---------- ----------- -------------------------...---
 1     Make Service reports (SRV)         No         Every day   Scheduled to run at ...
 2     Make Sales invoices (SLS)          No         Every day   Scheduled to run at ...
 3     Make Subscription invoices (SUB)   No         Every day   Scheduled to run at ...
===== ================================== ========== =========== =========================...===
<BLANKLINE>




These are the :term:`invoice generators <invoice generator>` in Noi:

>>> pprint(rt.models_by_base(invoicing.InvoiceGenerator))
[<class 'lino_xl.lib.storage.models.Filler'>,
 <class 'lino_xl.lib.subscriptions.models.SubscriptionPeriod'>,
 <class 'lino_xl.lib.trading.models.InvoiceItem'>,
 <class 'lino_xl.lib.working.models.Session'>]

Note that the ``reporting`` area should run one day *before* the ``default``
area.

- Subscription invoices get created based on the subscription periods (which in
  turn get created as summary data of the actual subscriptions one per year or
  month).
- Sales invoices get created based on service reports and storage fillers.
- Service reports get created based on working sessions.


>>> rt.show('invoicing.FollowUpRules')
===== ====================================================== ====================== ================
 No.   Invoicing task                                         Invoice generator      Source journal
----- ------------------------------------------------------ ---------------------- ----------------
 1     Invoicing task #1 (Make Service reports (SRV))         Working session
 2     Invoicing task #3 (Make Subscription invoices (SUB))   Subscription period
 3     Invoicing task #2 (Make Sales invoices (SLS))          Storage filler
 4     Invoicing task #2 (Make Sales invoices (SLS))          Trading invoice item
===== ====================================================== ====================== ================
<BLANKLINE>




#5386 (detail link on a ledger movement causes traceback)
=========================================================

>>> obj = rt.models.trading.VatProductInvoice.objects.filter(partner=1).last()
>>> obj
VatProductInvoice #104 ('SLS 8/2015')
>>> obj.partner
Partner #1 ('Rumma & Ko OÜ')
>>> rt.show('trading.ItemsByInvoice', obj)
==================== ============================================ ========= =========== ==== ============ ====================================================
 Product              Designation                                  UPr       Qty         D%   Amount       Invoiced object
-------------------- -------------------------------------------- --------- ----------- ---- ------------ ----------------------------------------------------
                      Filler Rumma & Ko OÜ Purchased Hourly rate                                           `Filler Rumma & Ko OÜ Purchased Hourly rate <…>`__
 Hourly rate          Hourly rate                                  60,0000   15:34            934,00
 **Total (2 rows)**                                                          **15:34**        **934,00**
==================== ============================================ ========= =========== ==== ============ ====================================================
<BLANKLINE>


>>> ar = rt.login("robin")
>>> rnd = settings.SITE.kernel.default_renderer

The default table for a :class:`trading.VatProductInvoice` is
:class:`trading.Invoices`:

>>> obj.__class__.get_default_table()
lino_xl.lib.trading.ui.Invoices

The detail_link of an invoice points to :class:`trading.InvoicesByJournal`
because the `detail_layout` to use depends on the journal's voucher type.

>>> obj.get_detail_action(ar)
<BoundAction(trading.InvoicesByJournal, <lino.core.actions.ShowDetail detail ('Detail')>)>

The following link is actually broken because it doesn't specify the master
instance (the journal) to InvoicesByJournal:

>>> print(rnd.obj2url(ar, obj))
javascript:window.App.runAction({ "action_full_name": "trading.Invoices.detail", "actorId": "trading.InvoicesByJournal", "rp": null, "status": { "record_id": 104 } })

>>> print(rnd.obj2htmls(ar, obj))
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE -SKIP
<a href="javascript:window.App.runAction({ &quot;action_full_name&quot;: &quot;trading.Invoices.detail&quot;,
&quot;actorId&quot;: &quot;trading.InvoicesByJournal&quot;,
&quot;rp&quot;: null, &quot;status&quot;: { &quot;record_id&quot;: 104 } })"
style="text-decoration:none">SLS 8/2015</a>



>>> for wm in obj.get_wanted_movements():
...     print(wm.__class__, wm.product)
<class 'lino_xl.lib.storage.models.Movement'> Hourly rate
<class 'lino_xl.lib.accounting.models.Movement'> None
<class 'lino_xl.lib.accounting.models.Movement'> None


..
  >>> dbhash.check_virgin()
