.. doctest docs/apps/noi/ddh.rst
.. _noi.specs.ddh:

=============================
Deletion handlers in Lino Noi
=============================

.. contents::
  :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.noi1e.startup import *


Here is a list of foreign keys in :ref:`noi` and their on_delete
behaviour. See also :ref:`dev.delete`.

>>> from lino.utils.diag import analyzer
>>> print(analyzer.show_foreign_keys())
... #doctest: +NORMALIZE_WHITESPACE +REPORT_UDIFF
- accounting.Account :
  - PROTECT : accounting.Journal.account, accounting.MatchRule.account, accounting.Movement.account, vat.InvoiceItem.account
- accounting.Journal :
  - CASCADE : accounting.MatchRule.journal, invoicing.FollowUpRule.source_journal
  - PROTECT : accounting.Voucher.journal, invoicing.Task.target_journal, storage.TransferRule.journal
- accounting.PaymentTerm :
  - PROTECT : trading.TradingRule.payment_term, trading.VatProductInvoice.payment_term, vat.VatAccountInvoice.payment_term
- accounting.Voucher :
  - CASCADE : accounting.Movement.voucher, storage.Movement.voucher
  - PROTECT : storage.DeliveryNote.voucher_ptr, subscriptions.Subscription.voucher_ptr, trading.VatProductInvoice.voucher_ptr, vat.VatAccountInvoice.voucher_ptr
  - SET_NULL : invoicing.Item.invoice
- cal.Calendar :
  - CASCADE : cal.Subscription.calendar, google.CalendarSubscription.calendar
  - PROTECT : cal.Room.calendar, system.SiteConfig.site_calendar
- cal.Event :
  - CASCADE : cal.Guest.event
  - PROTECT : cal.EntryRepeater.cal_entry
- cal.EventType :
  - PROTECT : cal.Event.event_type, cal.EventPolicy.event_type, cal.RecurrentEvent.event_type, system.SiteConfig.default_event_type, users.User.event_type
- cal.GuestRole :
  - PROTECT : cal.Guest.role
- cal.Room :
  - PROTECT : cal.Event.room
- comments.Comment :
  - CASCADE : comments.Reaction.comment, notify.Message.reply_to
  - PROTECT : comments.Comment.reply_to
- comments.CommentType :
  - PROTECT : comments.Comment.comment_type
- contacts.Company :
  - PROTECT : accounting.Journal.partner, cal.Event.company, cal.Room.company, contacts.Role.company, excerpts.Excerpt.company, peppol.Supplier.company
- contacts.CompanyType :
  - PROTECT : contacts.Company.type
- contacts.Partner :
  - CASCADE : addresses.Address.partner, contacts.Company.partner_ptr, contacts.Person.partner_ptr, invoicing.Item.partner, lists.Member.partner, phones.ContactDetail.partner, sepa.Account.partner, trading.TradingRule.partner
  - PROTECT : accounting.Movement.partner, invoicing.Plan.partner, storage.DeliveryNote.partner, storage.Filler.partner, storage.Movement.partner, storage.Provision.partner, subscriptions.Subscription.partner, trading.TradingRule.invoice_recipient, trading.VatProductInvoice.partner, users.User.partner, vat.VatAccountInvoice.partner
- contacts.Person :
  - CASCADE : google.Contact.contact
  - PROTECT : cal.Event.contact_person, cal.Guest.partner, cal.Room.contact_person, contacts.Role.person, excerpts.Excerpt.contact_person, tickets.Ticket.end_user
- contacts.RoleType :
  - PROTECT : cal.Event.contact_role, cal.Room.contact_role, contacts.Role.type, excerpts.Excerpt.contact_role
- contenttypes.ContentType :
  - PROTECT : accounting.Journal.default_invoiceable_type, cal.Event.owner_type, cal.Task.owner_type, changes.Change.master_type, changes.Change.object_type, checkdata.Message.owner_type, comments.Comment.owner_type, excerpts.Excerpt.owner_type, excerpts.ExcerptType.content_type, google.FailedForeignItem.item_class, invoicing.FollowUpRule.invoice_generator, invoicing.Item.generator_type, memo.Mention.owner_type, memo.Mention.target_type, notify.Message.owner_type, storage.DeliveryItem.invoiceable_type, topics.Tag.owner_type, trading.InvoiceItem.invoiceable_type, uploads.Upload.owner_type
- countries.Country :
  - PROTECT : addresses.Address.country, contacts.Partner.country, countries.Place.country
- countries.Place :
  - PROTECT : addresses.Address.city, addresses.Address.region, contacts.Partner.city, contacts.Partner.region, countries.Place.parent
- excerpts.Excerpt :
  - SET_NULL : storage.DeliveryNote.printed_by, subscriptions.Subscription.printed_by, trading.VatProductInvoice.printed_by
- excerpts.ExcerptType :
  - PROTECT : excerpts.Excerpt.excerpt_type
- google.CalendarSubscription :
  - PROTECT : google.EventSyncToken.subscription
- google.SyncSummary :
  - PROTECT : google.FailedForeignItem.job
- groups.Group :
  - CASCADE : groups.Membership.group
  - PROTECT : tickets.Ticket.group
- invoicing.Plan :
  - CASCADE : invoicing.Item.plan
- invoicing.Task :
  - CASCADE : invoicing.FollowUpRule.invoicing_task
  - PROTECT : invoicing.Plan.invoicing_task
- lists.List :
  - CASCADE : lists.Member.list
- lists.ListType :
  - PROTECT : lists.List.list_type
- periods.StoredPeriod :
  - PROTECT : accounting.Voucher.accounting_period
- periods.StoredYear :
  - PROTECT : accounting.Voucher.fiscal_year, periods.StoredPeriod.year
- products.Category :
  - PROTECT : products.Category.parent, products.Product.category
- products.Product :
  - PROTECT : invoicing.Tariff.product, products.PriceRule.product, storage.Component.child, storage.Component.parent, storage.DeliveryItem.product, storage.Filler.provision_product, storage.Movement.product, storage.Provision.product, subscriptions.Subscription.invoiceable_product, subscriptions.SubscriptionItem.product, trading.InvoiceItem.product, working.ReportingRule.product
- sepa.Account :
  - PROTECT : accounting.Journal.sepa_account
- storage.DeliveryNote :
  - CASCADE : storage.DeliveryItem.voucher
- subscriptions.Subscription :
  - CASCADE : subscriptions.SubscriptionItem.voucher, working.OrderSummary.master
  - PROTECT : invoicing.Plan.order, subscriptions.SubscriptionPeriod.master, tickets.Ticket.order
- tickets.Ticket :
  - CASCADE : nicknames.Naming.named
  - PROTECT : tickets.CheckListItem.ticket, tickets.Ticket.duplicate_of, tickets.Ticket.parent, working.Session.ticket
- tickets.TicketType :
  - PROTECT : tickets.Ticket.ticket_type
- topics.Topic :
  - PROTECT : topics.Interest.topic, topics.Tag.topic
- trading.PaperType :
  - PROTECT : subscriptions.Subscription.paper_type, trading.TradingRule.paper_type, trading.VatProductInvoice.paper_type
- trading.VatProductInvoice :
  - CASCADE : trading.InvoiceItem.voucher
- uploads.UploadType :
  - PROTECT : uploads.Upload.type
- uploads.Volume :
  - PROTECT : accounting.Journal.uploads_volume, uploads.Upload.volume
- users.User :
  - CASCADE : accounting.LedgerInfo.user, cal.Subscription.user, comments.Reaction.user, google.CalendarSubscription.user, groups.Membership.user, nicknames.Naming.user, notify.Subscription.user, topics.Interest.partner, working.UserSummary.master
  - PROTECT : accounting.Voucher.user, cal.Event.assigned_to, cal.Event.user, cal.RecurrentEvent.user, cal.Task.user, changes.Change.user, checkdata.Message.user, comments.Comment.user, dashboard.Widget.user, excerpts.Excerpt.user, google.CalendarSyncToken.user, google.Contact.user, google.ContactSyncToken.user, google.DeletedContact.user, google.DeletedEntry.user, google.EventSyncToken.user, google.SyncSummary.user, invoicing.Plan.user, invoicing.Task.user, notify.Message.user, social_django.UserSocialAuth.user, tickets.Ticket.assigned_to, tickets.Ticket.last_commenter, tickets.Ticket.reporter, tickets.Ticket.user, tinymce.TextFieldTemplate.user, uploads.Upload.user, users.Authority.authorized, users.Authority.user, working.Contract.user, working.Session.user
- vat.VatAccountInvoice :
  - CASCADE : vat.InvoiceItem.voucher
- working.SessionType :
  - PROTECT : products.PriceRule.selector, working.Session.session_type
<BLANKLINE>


Deleting
========

>>> d = get_json_dict('robin', "contacts/Companies/1", an='delete_selected', sr=1)
>>> print(d['message'])
Cannot delete Partner Rumma & Ko OÜ because 14 Movements refer to it.

>>> d = get_json_dict('robin', "contacts/Persons/68", an='delete_selected', sr=68)
>>> print(d['message'])
You are about to delete 1 Person
(Otto Östges)
as well as all related volatile records (1 Address, 1 List membership, 1 Trading rule). Are you sure?

>>> d = get_json_dict('robin', "lists/Lists/1", an='delete_selected', sr=1)
>>> print(d['message'])
You are about to delete 1 Partner List
(Announcements)
as well as all related volatile records (12 List memberships). Are you sure?
