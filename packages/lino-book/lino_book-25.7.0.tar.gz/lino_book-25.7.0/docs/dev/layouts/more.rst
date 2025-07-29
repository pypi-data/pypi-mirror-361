.. doctest docs/dev/layouts/more.rst
.. _dev.layouts.more:

==================
More about layouts
==================

.. contents::
    :depth: 2
    :local:

The ``detail_layout`` attribute
===============================

The :attr:`detail_layout` is normally an instance of
:class:`DetailLayout <lino.core.layouts.DetailLayout>` or a
subclass thereof.  For example::

    class FooDetail(dd.DetailLayout):
        ...

    class Foos(dd.Table):
        ...
        detail_layout = FooDetail()

It is possible and recommended to specify :attr:`detail_layout` as
a string, in which case it will be resolved at startup as follows:

If the string contains at least one newline (or no newline and
also no dot) then it is taken as the :attr:`main` of a
:class:`DetailLayout <lino.core.layouts.DetailLayout>`.
For example::

    class Foos(dd.Table):
        ...
        detail_layout = """
        id name
        description
        """

If the string contains a dot ('.') and *does not contain* any
newlines, then Lino takes this as the name of the class to be
instantiated and used.

For example::

    class Courses(dd.Table):
        ...
        detail_layout = 'courses.CourseDetail'

This feature makes it possible to override the detail layout in an
extended plugin. Before this you had to define a new class and to
assign an instance of that class to every actor which uses it.
But e.g. in :mod:`lino_xl.lib.courses` we have a lot of subclasses
of the :class:`Courses` actor.


Class-based detail layouts
==========================

Code examples in this document are taken from :doc:`/dev/lets/index` unless
otherwise specified. 

You can define a detail window by setting the :attr:`detail_layout
<lino.core.actors.Actor.detail_layout>` attribute directly as a multi-line text
containing the names of data elements, as in the following example::

    class Members(dd.Table):
        ...
        detail_layout = """
        id name place email
        OffersByMember DemandsByMember
        """

Result:

.. image:: ../lets/b.png
  :scale: 50 %


But you can get the same result by saying::

    class MemberDetail(dd.DetailLayout):
        main = """
        id name place email
        OffersByMember DemandsByMember
        """

    class Members(dd.Table):
        ...
        detail_layout = "lets.Members"

This syntax is slightly more verbose but has several advantages:

- It lets you define "panels" in order to group the fields on your window.
- It lets you define :term:`tabbed detail layouts <tabbed detail layout>`.
- It makes it more easy to override the layout by plugins that inherit from your
  plugin.

A :term:`detail layout` becomes **tabbed** when its :attr:`main` attribute has
only one row of layout elements.

.. glossary::

  tabbed detail layout

    A :term:`detail layout` that has a series of tabs.

The elements mentioned in the :attr:`main` attribute of a tabbed detail layout
must have labels, which become the label of their tab. They don't need to be
panels: they can be a :term:`slave table` or a text field.

For example, the detail layout of a :term:`site user` in `step 4` is a
:term:`tabbed detail layout` with two tabs, labelled "General" and
"Preferences":

.. image:: /images/screenshots/lets4.users.UserDetail.general.png
  :width: 45 %

.. image:: /images/screenshots/lets4.users.UserDetail.contact.png
  :width: 45 %

Here is the source code used to define this::

  from lino.modlib.users.ui import *

  class UserDetail(UserDetail):

      main = "general contact"

      general = dd.Panel("""
      first_name last_name initials
      place
      market.DemandsByCustomer market.OffersByProvider
      """, label=_("General"))

      contact = dd.Panel("""
      box1
      remarks:40 users.AuthoritiesGiven:20
      """, label=_("Preferences"))

      box1 = """
      username user_type:20
      language time_zone
      id created modified
      """

Note that the ``general`` and ``contacts`` are tab panels defined by
instantiating the :class:`dd.Panel` class while ``box1`` is a simple panel that
needs no label.

Another example is the detail layout of a
:class:`lino_xl.lib.trading.VatProductInvoice`:

.. image:: /images/screenshots/sales.Invoicedetail.png
  :width: 80 %

Here is the source code used to define this layout::

  class InvoiceDetail(dd.DetailLayout):
      main = "general more accounting"

      general = dd.Panel("""
      panel1:30 panel3:30 panel2 totals:20
      ItemsByInvoice
      """, label=_("General"))

      more = dd.Panel("""
      id user language #project #item_vat
      intro
      """, label=_("More"))

      accounting = dd.Panel("""
      journal accounting_period number #narration
      vat.MovementsByVoucher
      """, label=_("Ledger"))

      totals = dd.Panel("""
      total_base
      total_vat
      total_incl
      workflow_buttons
      """)

      panel1 = dd.Panel("""
      entry_date
      #order subject
      payment_term
      due_date:20
      """)

      panel2 = dd.Panel("""
      partner
      subject
      vat_regime
      your_ref match
      """)

      panel3 = dd.Panel("""
      payment_method
      paper_type
      printed
      """)




Combined list and detail view
=============================

When you add a :attr:`navigator_panel` to a :term:`detail layout`, it can make
sense to "skip the list window" by setting the default action of a table view to
detail.  Examples:

Or the detail layout of :class:`lino_xl.lib.contacts.Person` in :ref:`amici`::

  class PersonDetail(PersonDetail):

      main = "general #contact family more"

      general = dd.Panel("navigation_panel:20 general_box:60", label=_("General"))

      general_box = """
      overview contact_box #phones.ContactDetailsByPartner
      contacts.RolesByPerson:30 lists.MembersByPartner:30 cal.EntriesByGuest:30
      """

      contact_box = dd.Panel("""
      last_name first_name:15
      gender #title:10 language:10
      birth_date age:10 id:6
      """)  #, label=_("Contact"))

      family = dd.Panel("""
      humanlinks.LinksByHuman:50 households.MembersByPerson:30
      households.SiblingsByPerson
      """, label=_("Family"))

      more = dd.Panel("""
      ... comments.CommentsByRFC:30
      """, label=_("More"))



The tree navigator
==================

The :attr:`lino.mixins.sequenced.Hierarchical.treeview_panel` is used to add a
tree navigation view.
