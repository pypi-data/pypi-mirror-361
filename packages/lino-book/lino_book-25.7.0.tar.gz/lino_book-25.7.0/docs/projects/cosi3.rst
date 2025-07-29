.. doctest docs/projects/cosi3.rst
.. _book.specs.cosi3:

==============================================
``cosi3`` : A Lino Così for Estonia
==============================================

This :term:`demo project` shows a :ref:`cosi` site for a small company in
Estonia.

It uses :mod:`lino_xl.lib.eevat`, the VAT plugin for Estonia.
It imports every place in Estonia from :mod:`commondata.ee`.
It also shows invoices with a customized
:data:`page_background_image <lino.modlib.weasyprint.page_background_image>`

This project is also the first to demonstrate the  :mod:`lino_xl.lib.assets`
plugin.

This page also shows that the translations to Estonian need some work, they are
less than 95% finished.


.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.cosi3.startup import *

>>> ses = rt.login("rando")
>>> dd.translation.activate('et')

>>> dd.plugins.weasyprint.page_background_image  #doctest: +ELLIPSIS
'...lino_book/projects/cosi3/config/weasyprint/page-background.png'


>>> dd.plugins.vat.declaration_plugin
'lino_xl.lib.eevat'


>>> settings.SITE.with_assets
True

>>> from lino.utils.sums import myround
>>> from decimal import Decimal
>>> myround(Decimal(57.89532))
Decimal('57.90')


Places in Estonia
=================

The Estonian `Wikipedia
<https://et.wikipedia.org/wiki/Rapla_maakond>`_ says:

    Rapla maakonnas on 10 omavalitsusüksust (valda):

    Juuru vald - Järvakandi vald - Kaiu vald - Kehtna vald - Kohila vald - Käru vald - Märjamaa vald - Raikküla vald - Rapla vald - Vigala vald

Lino and :mod:`commondata.ee` agree with this:

>>> raplamaa = countries.Place.objects.get(
...    name="Rapla", type=countries.PlaceTypes.county)
>>> ses.show("countries.PlacesByPlace", raplamaa)
==================== =========== ==========
 Asum                 Asumiliik   zip code
-------------------- ----------- ----------
 `Juuru <…>`__        Vald
 `Järvakandi <…>`__   Vald
 `Kaiu <…>`__         Vald
 `Kehtna <…>`__       Vald
 `Kohila <…>`__       Vald
 `Käru <…>`__         Vald
 `Märjamaa <…>`__     Vald
 `Raikküla <…>`__     Vald
 `Rapla <…>`__        Linn
 `Vigala <…>`__       Vald
==================== =========== ==========
<BLANKLINE>


Another test is the
`municipality of Juuru
<https://et.wikipedia.org/wiki/Juuru_vald>`_ for which Wikipedia
announces one small borough and 14 villages:

    Juuru vallas on üks alevik (Juuru, elanikke 597) ja 14 küla: Atla (91),
    Helda, Hõreda (80), Härgla (84), Jaluse (40), Järlepa (235), Kalda, Lõiuse
    (103), Mahtra (99), Maidla (124), Orguse (43), Pirgu (102), Sadala ja Vankse
    (30).

Lino and :mod:`commondata` again agree with this:

>>> juuru = countries.Place.objects.get(name="Juuru",
...    type=countries.PlaceTypes.municipality)
>>> ses.show("countries.PlacesByPlace", juuru)
================= =========== ==========
 Asum              Asumiliik   zip code
----------------- ----------- ----------
 `Atla <…>`__      Küla        79403
 `Helda <…>`__     Küla        79417
 `Härgla <…>`__    Küla        79404
 `Hõreda <…>`__    Küla        79010
 `Jaluse <…>`__    Küla        79410
 `Juuru <…>`__     Alevik
 `Järlepa <…>`__   Küla
 `Kalda <…>`__     Küla        79418
 `Lõiuse <…>`__    Küla        79405
 `Mahtra <…>`__    Küla        79407
 `Orguse <…>`__    Küla
 `Pirgu <…>`__     Küla
 `Sadala <…>`__    Küla        79419
 `Vankse <…>`__    Küla        79406
================= =========== ==========
<BLANKLINE>


Formatting postal addresses
---------------------------


The country is being printed in the address, depends on the
:attr:`country_code <Plugin.country_code>` setting.

>>> rmu(dd.plugins.countries.country_code)
'EE'
>>> dd.plugins.countries.get_my_country()
Country #EE ('Eesti')



>>> eesti = countries.Country.objects.get(isocode="EE")
>>> sindi = countries.Place.objects.get(name="Sindi")
>>> p = contacts.Person(first_name="Malle", last_name="Mets",
...     street="Männi tn", street_no="5", street_box="-6",
...     zip_code="86705", country=eesti, city=sindi)
>>> print(p.address)
Malle Mets
Männi tn 5-6
86705 Sindi

Townships in Estonia get special handling: their name is replaced by
the town's name when a zip code is known:

>>> city = countries.Place.objects.get(name="Kesklinn")
>>> print(city)
Kesklinn
>>> city.type
<countries.PlaceTypes.township:55>
>>> p = contacts.Person(first_name="Kati", last_name="Kask",
...     street="Tartu mnt", street_no="71", street_box="-5",
...     zip_code="10115", country=eesti, city=city)
>>> print(p.address)
Kati Kask
Tartu mnt 71-5
10115 Tallinn

And yet another rule for countryside addresses:

>>> city = countries.Place.objects.get(name="Vana-Vigala")
>>> city.type
<countries.PlaceTypes.village:70>
>>> p = contacts.Person(first_name="Kati", last_name="Kask",
...     street="Hirvepargi", street_no="123",
...     zip_code="78003", country=eesti, city=city)
>>> print(p.address)
Kati Kask
Hirvepargi 123
Vana-Vigala küla
Vigala vald
78003 Rapla maakond

.. _dg.projects.cosi3.settings:

Some examples for customizing the trading plugin
================================================

.. currentmodule:: lino_xl.lib.trading

The ``cosi3`` demo project has a customized :data:`items_column_names` for its
:class:`ItemsByInvoice` table, which uses absolute instead of relative discounts.
It also shows how to use :meth:`lino.core.model.Model.update_field` change the
number of decimal positions of a price field.

The :xfile:`settings.py` file says::

    def get_plugin_configs(self):
        ...
        yield ("trading", "items_column_names",
               "product unit_price qty discount_amount amount invoiceable *")

    def do_site_startup(self):
        # change the number of decimal places from 4 to 2:
        update_field = self.models.trading.InvoiceItem.update_field
        update_field('unit_price', decimal_places=2)
        update_field('total_base', decimal_places=2)
        ...

Result:

>>> dd.plugins.trading.items_column_names
'product invoiceable_id qty amount discount_amount unit_price *'


>>> # obj = trading.VatProductInvoice.objects.filter(partner=1).last()
>>> obj = trading.VatProductInvoice.objects.last()
>>> obj
VatProductInvoice #208 ('SLS 25/2024')
>>> obj.partner
Partner #76 ('Heinsalu Ivo')
>>> rt.show('trading.ItemsByInvoice', obj)
==================== ======= ======== ============== ============= ========
 Toode                Plate   Qty      Summa          Allahindlus   UPr
-------------------- ------- -------- -------------- ------------- --------
 Laud metallist               10       1 299,90                     129,99
 == Vahesumma ==              10       1 299,90
 Tool metallist               8        639,92                       79,99
 Majutus 1MB/s                4        15,96                        3,99
 == Vahesumma ==              12       655,88
 **Kokku (5 rida)**           **44**   **3 911,56**
==================== ======= ======== ============== ============= ========
<BLANKLINE>


Parent layouts
==============

Lino has a utility function :func:`lino.api.doctest.show_parent_layouts`. The
idea was introduced to implement customizable ``column_names`` for the items of
an invoice. We then didn't use it but thought that the idea itself deserves
further exploration.

>>> show_parent_layouts()
======================================== =========================
 actor                                    is used in
---------------------------------------- -------------------------
 accounting.MatchRulesByJournal           accounting.Journals
 accounting.MovementsByAccount            accounting.Accounts
 accounting.MovementsByPartner            contacts.Partners
 accounting.MovementsByProject            contacts.Partners
 accounting.MovementsByVoucher            finan.BankStatements
 assets.AssetsByPartner                   contacts.Partners
 checkdata.MessagesByChecker              checkdata.Checkers
 contacts.PartnersByCity                  countries.Places
 contacts.RolesByCompany                  contacts.Companies
 contacts.RolesByPerson                   contacts.Persons
 countries.PlacesByCountry                countries.Countries
 countries.PlacesByPlace                  countries.Places
 excerpts.ExcerptsByType                  excerpts.ExcerptTypes
 finan.ItemsByBankStatement               finan.BankStatements
 finan.ItemsByJournalEntry                finan.FinancialVouchers
 finan.ItemsByPaymentOrder                finan.PaymentOrders
 gfks.BrokenGFKsByModel                   gfks.ContentTypes
 invoicing.ItemsByPlan                    invoicing.Plans
 invoicing.RulesByTask                    invoicing.Tasks
 products.ProductsByCategory              products.Categories
 sepa.AccountsByPartner                   contacts.Partners
 sheets.MovementsByItemEntry              sheets.ItemEntries
 trading.InvoiceItemsByProduct            products.BaseProducts
 trading.InvoicesByPartner                contacts.Partners
 trading.ItemsByInvoice                   trading.Invoices
 trading.ItemsByInvoicePrint              trading.Invoices
 trading.ItemsByInvoicePrintNoQtyColumn   trading.Invoices
 trading.RulesByPartner                   contacts.Companies
 uploads.UploadsByController              finan.BankStatements
 uploads.UploadsByType                    uploads.UploadTypes
 uploads.UploadsByVolume                  uploads.Volumes
 users.AuthoritiesGiven                   users.Users
 users.AuthoritiesTaken                   users.Users
 vat.ItemsByInvoice                       vat.Invoices
 vat.MovementsByDeclaration               eevat.Declarations
 vat.MovementsByVoucher                   vat.Invoices
 vat.PurchasesByDeclaration               eevat.Declarations
 vat.SalesByDeclaration                   eevat.Declarations
 vat.VouchersByPartner                    contacts.Partners
======================================== =========================
<BLANKLINE>
