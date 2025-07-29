.. doctest docs/apps/cosi/index.rst
.. _specs.cosi:
.. _cosi.tested:

=========================
Lino Così Developer Guide
=========================

This is the developer documentation for :ref:`cosi`.


.. toctree::
    :maxdepth: 1

    tim2lino
    invoicing



.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.cosi1.startup import *


Overviews
=========

>>> show_choosers()
============================================= ============================ ===================
 field                                         context_fields               can_create_choice
--------------------------------------------- ---------------------------- -------------------
 accounting.Account.sheet_item                                              False
 accounting.Journal.template                   build_method, voucher_type   False
 accounting.Journal.default_invoiceable_type                                False
 accounting.Movement.match                     partner, account             False
 accounting.Voucher.journal                                                 False
 bevat.Declaration.journal                                                  False
 checkdata.Message.owner_id                    owner_type                   False
 contacts.Company.country                                                   False
 contacts.Company.city                         country, region              True
 contacts.Company.region                       country                      False
 contacts.Company.vat_regime                   country                      False
 contacts.Company.municipality                                              False
 contacts.Partner.country                                                   False
 contacts.Partner.city                         country, region              True
 contacts.Partner.region                       country                      False
 contacts.Partner.vat_regime                   country                      False
 contacts.Partner.municipality                                              False
 contacts.Person.country                                                    False
 contacts.Person.city                          country, region              True
 contacts.Person.region                        country                      False
 contacts.Person.vat_regime                    country                      False
 contacts.Person.municipality                                               False
 contacts.Role.person                                                       True
 countries.Place.type                          country                      False
 excerpts.Excerpt.contact_person               company                      True
 excerpts.Excerpt.owner_id                     owner_type                   False
 excerpts.Excerpt.excerpt_type                 owner                        False
 excerpts.ExcerptType.template                 build_method, content_type   False
 excerpts.ExcerptType.email_template           content_type                 False
 excerpts.ExcerptType.body_template            content_type                 False
 finan.BankStatement.journal                                                False
 finan.BankStatementItem.match                 voucher, partner             False
 finan.JournalEntry.journal                                                 False
 finan.JournalEntryItem.match                  voucher, partner             False
 finan.PaymentOrder.journal                                                 False
 finan.PaymentOrderItem.match                  voucher, partner             False
 finan.PaymentOrderItem.bank_account           partner, project             False
 invoicing.FollowUpRule.invoice_generator      invoicing_task               False
 invoicing.FollowUpRule.source_journal         invoicing_task               False
 invoicing.Item.generator_id                   generator_type               False
 invoicing.Task.procedure                                                   False
 linod.SystemTask.procedure                                                 False
 memo.Mention.owner_id                         owner_type                   False
 memo.Mention.target_id                        target_type                  False
 notify.Message.owner_id                       owner_type                   False
 products.Product.category                     product_type                 False
 trading.InvoiceItem.invoiceable_type                                       False
 trading.InvoiceItem.invoiceable_id            invoiceable_type, voucher    True
 trading.PaperType.template                                                 False
 trading.VatProductInvoice.journal                                          False
 trading.VatProductInvoice.match               journal, partner             False
 trading.VatProductInvoice.vat_regime          partner                      False
 uploads.Upload.owner_id                       owner_type                   False
 uploads.Upload.type                           upload_area                  False
 uploads.Upload.library_file                   volume                       False
 users.Authority.authorized                    user                         False
 vat.InvoiceItem.account                       voucher                      False
 vat.VatAccountInvoice.journal                                              False
 vat.VatAccountInvoice.match                   journal, partner             False
 vat.VatAccountInvoice.vat_regime              partner                      False
============================================= ============================ ===================
<BLANKLINE>
