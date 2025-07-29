.. doctest docs/apps/noi/users.rst
.. _noi.specs.user:

======================================
``users`` in Noi
======================================

.. currentmodule:: lino_noi.lib.users

The :mod:`lino_noi.lib.users` plugin extends :mod:`lino.modlib.users` for Lino
Noi.


.. contents::
  :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.noi1e.startup import *


Here are the users of the demo site.

>>> rt.show('users.UsersOverview')
========== ===================== ==========
 Username   User type             Language
---------- --------------------- ----------
 jean       400 (Developer)       en
 luc        400 (Developer)       en
 marc       100 (Customer)        en
 mathieu    200 (Contributor)     en
 robin      900 (Administrator)   en
 rolf       900 (Administrator)   de
 romain     900 (Administrator)   fr
========== ===================== ==========
<BLANKLINE>


User types
==========

A :ref:`noi` site has the following user types:

>>> rt.show(users.UserTypes)
======= =============== ===============
 value   name            text
------- --------------- ---------------
 000     anonymous       Anonymous
 100     customer user   Customer
 200     contributor     Contributor
 400     developer       Developer
 900     admin           Administrator
======= =============== ===============
<BLANKLINE>

Note that "Customer" has two internal names.

>>> users.UserTypes.customer is users.UserTypes.user
True

.. currentmodule:: lino_noi.lib.noi

.. class:: UserTypes

  .. attribute:: user

    An alias for :attr:`customer`.

  .. attribute:: customer

    Somebody who uses some part of the software being developed by
    the team. This is usually the contact person of a customer.

  .. attribute:: contributor

    Can submit tickets, work on them and discuss with other team members.  Does
    not see confidential data nor the tickets of other teams.

  .. attribute:: developer

    A trusted contributor who can do almost everything except managing other
    users.

  .. attribute:: admin

    Can see everything including create new :term:`end users <end user>`, change
    their passwords, assign them to teams.

Here is a list of user types of those who can work on tickets:

>>> from lino_xl.lib.working.roles import Worker
>>> UserTypes = rt.models.users.UserTypes
>>> [p.name for p in UserTypes.items()
...     if p.has_required_roles([Worker])]
['contributor', 'developer', 'admin']

And here are those who don't work:

>>> [p for p in UserTypes.get_list_items()
...    if not p.has_required_roles([Worker])]
[<users.UserTypes.anonymous:000>, <users.UserTypes.customer:100>]


User roles and permissions
==========================

Here is the :class:`lino.modlib.users.UserRoles` table for :ref:`noi`:

>>> rt.show(users.UserRoles)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
================================ ===== ===== ===== ===== =====
 Name                             000   100   200   400   900
-------------------------------- ----- ----- ----- ----- -----
 accounting.LedgerStaff                                   ☑
 blogs.BlogsReader                      ☑     ☑     ☑     ☑
 cal.CalendarReader               ☑
 checkdata.CheckdataUser                      ☑     ☑     ☑
 comments.CommentsReader          ☑     ☑     ☑     ☑     ☑
 comments.CommentsStaff                             ☑     ☑
 comments.CommentsUser                  ☑     ☑     ☑     ☑
 comments.PrivateCommentsReader                     ☑     ☑
 contacts.ContactsStaff                                   ☑
 contacts.ContactsUser                              ☑     ☑
 core.DataExporter                      ☑     ☑     ☑     ☑
 core.Expert                                        ☑     ☑
 core.SiteUser                          ☑     ☑     ☑     ☑
 courses.CoursesUser                          ☑     ☑     ☑
 excerpts.ExcerptsStaff                             ☑     ☑
 excerpts.ExcerptsUser                        ☑     ☑     ☑
 invoicing.InvoicingStaff                                 ☑
 invoicing.InvoicingUser                                  ☑
 noi.Anonymous                    ☑
 noi.Contributor                              ☑     ☑     ☑
 noi.Customer                           ☑     ☑     ☑     ☑
 noi.Developer                                      ☑     ☑
 noi.SiteAdmin                                            ☑
 office.OfficeStaff                                       ☑
 office.OfficeUser                      ☑     ☑     ☑     ☑
 polls.PollsAdmin                                         ☑
 polls.PollsStaff                             ☑     ☑     ☑
 polls.PollsUser                        ☑     ☑     ☑     ☑
 products.ProductsStaff                                   ☑
 storage.StorageStaff                                     ☑
 storage.StorageUser                                      ☑
 tickets.Reporter                       ☑     ☑     ☑     ☑
 tickets.Searcher                 ☑     ☑     ☑     ☑     ☑
 tickets.TicketsStaff                               ☑     ☑
 tickets.Triager                                    ☑     ☑
 topics.TopicsUser                      ☑     ☑     ☑     ☑
 votes.VotesStaff                                         ☑
 votes.VotesUser                        ☑     ☑     ☑     ☑
 working.Worker                               ☑     ☑     ☑
================================ ===== ===== ===== ===== =====
<BLANKLINE>



Users
=====

The following shows a list of all windows in :ref:`noi`  and who can see them:

>>> print(analyzer.show_window_permissions())
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
- about.About.create_account : visible for all
- about.About.insert_reference : visible for all
- about.About.reset_password : visible for all
- about.About.show : visible for all
- about.About.sign_in : visible for all
- about.About.verify_user : visible for all
- accounting.Accounts.detail : visible for admin
- accounting.Accounts.insert : visible for admin
- accounting.Accounts.merge_row : visible for admin
- accounting.AllVouchers.detail : visible for admin
- accounting.Journals.detail : visible for admin
- accounting.Journals.insert : visible for admin
- accounting.Journals.merge_row : visible for admin
- accounting.PaymentTerms.detail : visible for admin
- accounting.PaymentTerms.merge_row : visible for admin
- addresses.Addresses.detail : visible for admin
- addresses.Addresses.insert : visible for admin
- cal.Calendars.detail : visible for admin
- cal.Calendars.insert : visible for admin
- cal.EntriesByGuest.insert : visible for customer contributor developer admin
- cal.EventTypes.detail : visible for admin
- cal.EventTypes.insert : visible for admin
- cal.EventTypes.merge_row : visible for admin
- cal.Events.detail : visible for all
- cal.Events.insert : visible for customer contributor developer admin
- cal.GuestRoles.detail : visible for admin
- cal.GuestRoles.merge_row : visible for admin
- cal.Guests.detail : visible for nobody
- cal.Guests.insert : visible for nobody
- cal.RecurrentEvents.detail : visible for admin
- cal.RecurrentEvents.insert : visible for admin
- cal.Rooms.detail : visible for admin
- cal.Rooms.insert : visible for admin
- cal.Tasks.detail : visible for admin
- cal.Tasks.insert : visible for admin
- calview.DailyView.detail : visible for customer contributor developer admin
- calview.MonthlyView.detail : visible for customer contributor developer admin
- calview.WeeklyView.detail : visible for customer contributor developer admin
- changes.Changes.detail : visible for admin
- checkdata.Checkers.detail : visible for admin
- checkdata.Messages.detail : visible for customer contributor developer admin
- comments.CommentTypes.detail : visible for developer admin
- comments.CommentTypes.insert : visible for developer admin
- comments.Comments.detail : visible for customer contributor developer admin
- comments.Comments.insert : visible for customer contributor developer admin
- comments.CommentsByRFC.insert : visible for customer contributor developer admin
- contacts.Companies.detail : visible for developer admin
- contacts.Companies.insert : visible for developer admin
- contacts.Companies.merge_row : visible for developer admin
- contacts.Partners.detail : visible for developer admin
- contacts.Partners.merge_row : visible for developer admin
- contacts.Persons.detail : visible for developer admin
- contacts.Persons.insert : visible for developer admin
- contacts.Persons.merge_row : visible for developer admin
- contacts.RolesByCompany.insert : visible for developer admin
- contacts.RolesByPerson.insert : visible for developer admin
- countries.Countries.detail : visible for admin
- countries.Countries.insert : visible for admin
- countries.Places.detail : visible for admin
- countries.Places.insert : visible for admin
- excerpts.ExcerptTypes.detail : visible for developer admin
- excerpts.ExcerptTypes.insert : visible for developer admin
- excerpts.Excerpts.detail : visible for contributor developer admin
- gfks.ContentTypes.detail : visible for admin
- google.MyContacts.insert : visible for customer contributor developer admin
- google.SyncSummaries.detail : visible for admin
- groups.Groups.detail : visible for admin
- groups.Groups.insert : visible for admin
- groups.Groups.merge_row : visible for admin
- groups.Memberships.detail : visible for admin
- groups.Memberships.insert : visible for admin
- invoicing.Plans.detail : visible for admin
- invoicing.Tasks.detail : visible for admin
- invoicing.Tasks.insert : visible for admin
- linod.SystemTasks.detail : visible for admin
- linod.SystemTasks.insert : visible for admin
- lists.Lists.detail : visible for developer admin
- lists.Lists.insert : visible for developer admin
- lists.Lists.merge_row : visible for developer admin
- lists.Members.detail : visible for developer admin
- lists.MembersByPartner.insert : visible for developer admin
- peppol.Suppliers.detail : visible for admin
- peppol.Suppliers.insert : visible for admin
- periods.StoredPeriods.merge_row : visible for admin
- periods.StoredYears.merge_row : visible for admin
- phones.ContactDetails.detail : visible for admin
- phones.ContactDetails.insert : visible for admin
- products.Categories.detail : visible for admin
- products.Products.detail : visible for admin
- products.Products.insert : visible for admin
- sepa.AccountsByPartner.insert : visible for developer admin
- storage.DeliveryNotes.detail : visible for admin
- storage.DeliveryNotesByJournal.insert : visible for admin
- storage.Fillers.detail : visible for admin
- subscriptions.SubscriptionItems.detail : visible for admin
- subscriptions.SubscriptionItems.insert : visible for admin
- subscriptions.Subscriptions.detail : visible for admin
- subscriptions.Subscriptions.insert : visible for admin
- subscriptions.Subscriptions.merge_row : visible for admin
- subscriptions.SubscriptionsByJournal.insert : visible for admin
- system.SiteConfigs.detail : visible for admin
- tickets.TicketTypes.detail : visible for developer admin
- tickets.Tickets.detail : visible for all
- tickets.Tickets.insert : visible for customer contributor developer admin
- tickets.Tickets.merge_row : visible for developer admin
- tickets.Tickets.spawn_ticket : visible for all
- tinymce.TextFieldTemplates.detail : visible for admin
- tinymce.TextFieldTemplates.insert : visible for admin
- topics.Interests.detail : visible for customer contributor developer admin
- topics.Interests.insert : visible for customer contributor developer admin
- topics.InterestsByPartner.insert : visible for customer contributor developer admin
- topics.TagsByOwner.insert : visible for customer contributor developer admin
- topics.Topics.detail : visible for customer contributor developer admin
- topics.Topics.insert : visible for customer contributor developer admin
- topics.Topics.merge_row : visible for developer admin
- trading.InvoiceItems.detail : visible for admin
- trading.InvoiceItems.insert : visible for admin
- trading.Invoices.detail : visible for admin
- trading.Invoices.insert : visible for admin
- trading.InvoicesByJournal.insert : visible for admin
- trading.PaperTypes.merge_row : visible for admin
- trading.TradingRules.detail : visible for admin
- uploads.UploadTypes.detail : visible for admin
- uploads.UploadTypes.insert : visible for admin
- uploads.Uploads.camera_stream : visible for customer contributor developer admin
- uploads.Uploads.detail : visible for customer contributor developer admin
- uploads.Uploads.insert : visible for customer contributor developer admin
- uploads.UploadsByController.insert : visible for customer contributor developer admin
- uploads.Volumes.detail : visible for admin
- uploads.Volumes.insert : visible for admin
- uploads.Volumes.merge_row : visible for admin
- users.AllUsers.change_password : visible for admin
- users.AllUsers.detail : visible for admin
- users.AllUsers.insert : visible for admin
- users.AllUsers.merge_row : visible for admin
- users.AllUsers.verify_me : visible for admin
- vat.Invoices.detail : visible for admin
- vat.Invoices.insert : visible for admin
- vat.InvoicesByJournal.insert : visible for admin
- vat.VouchersByPartner.detail : visible for admin
- working.OrderSummaries.detail : visible for customer contributor developer admin
- working.Sessions.detail : visible for contributor developer admin
- working.Sessions.insert : visible for contributor developer admin
- working.UserSummaries.detail : visible for customer contributor developer admin
- working.WorkedHours.detail : visible for customer contributor developer admin
<BLANKLINE>
