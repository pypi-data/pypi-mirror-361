.. _layouts_tutorial:

==========================
Some more layout examples
==========================

See :doc:`/dev/layouts/index`


Modal windows
=============

If you want a modal window (not a full-screen window), then you need
to specify the `window_size` keyword argument.  A simple FormLayout



Tabbed forms
============

If the ``main`` panel of a FormLayout is *horizontal* (i.e.)
doesn't contain any newline, then the Layout will be rendered
as a tabbed panel.

.. textimage:: layouts2.jpg layouts3.jpg layouts4.jpg
  :scale: 40 %

  ::

    class InvoiceDetail(dd.FormLayout):
        main = "general more accounting"

        totals = dd.Panel("""
        # discount
        total_base
        total_vat
        total_incl
        workflow_buttons
        """,label=_("Totals"))

        invoice_header = dd.Panel("""
        date partner vat_regime
        order subject your_ref
        payment_term due_date:20
        imode shipping_mode
        """,label=_("Header")) # sales_remark

        general = dd.Panel("""
        invoice_header:60 totals:20
        ItemsByInvoice
        """,label=_("General"))

        more = dd.Panel("""
        id user language project 
        intro
        """,label=_("More"))

        accounting = dd.Panel("""
        journal year number narration
        accounting.MovementsByVoucher
        """,label=_("Ledger"))

    class Invoices(TradingVouchers):
        ...
        detail_layout = InvoiceDetail()




Layouts and polymorphism
------------------------

:mod:`lino_xl.lib.contacts`
uses MTI to represent the fact that a Partner can be
either a Person or a Company.
here are the three resulting detail windows.


.. textimage:: mti1.jpg
  :scale: 30 %

  ::

    class PartnerDetail(dd.FormLayout):

        main = """
        address_box:60 contact_box:30
        bottom_box
        """

        address_box = dd.Panel("""
        name_box
        country region city zip_code:10
        addr1
        street_prefix street:25 street_no street_box
        addr2
        """,label = _("Address"))

        contact_box = dd.Panel("""
        info_box
        email:40
        url
        phone
        gsm fax
        """,label = _("Contact"))

        bottom_box = """
        remarks
        is_person is_company #is_user
        """

        name_box = "name"
        info_box = "id language"


.. textimage:: mti2.jpg
  :scale: 30 %

  ::

    class PersonDetail(PartnerDetail):

        name_box = "last_name first_name:15 gender title:10"
        info_box = "id:5 language:10"
        bottom_box = "remarks contacts.RolesByPerson"


.. textimage:: mti3.jpg
  :scale: 30 %

  ::

    class CompanyDetail(PartnerDetail):

        bottom_box = """
        type vat_id:12
        remarks contacts.RolesByCompany
        """




TODO: continue this tutorial.
