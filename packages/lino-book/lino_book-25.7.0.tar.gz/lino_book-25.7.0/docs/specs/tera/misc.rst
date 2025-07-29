.. doctest docs/specs/tera/misc.rst
.. _tera.specs.misc:
.. _presto.specs.psico:

=========================
Lino Tera : miscellaneous
=========================

.. contents::
   :local:
   :depth: 2

.. include:: /../docs/shared/include/tested.rst

>>> from lino import startup
>>> startup('lino_book.projects.tera1.settings')
>>> from lino.api.doctest import *
>>> from django.db import models


Every :ref:`tera` application has a :xfile:`settings.py` module that
inherits from :mod:`lino_tera.lib.tera.settings`.

>>> from lino_tera.lib.tera.settings import Site
>>> isinstance(settings.SITE, Site)
True

Lino Tera does not have multiple addresses per partner.

>>> dd.is_installed('addresses')
False


Partner types
=============

>>> dd.plugins.contacts
<lino_tera.lib.contacts.Plugin lino_tera.lib.contacts(needs ['lino_xl.lib.countries', 'lino.modlib.system'])>

>>> print([m.__name__ for m in rt.models_by_base(rt.models.contacts.Partner)])
['Company', 'Partner', 'Person', 'Household', 'Client']

.. py2rst::

   from lino import startup
   startup('lino_book.projects.tera1.settings')
   from lino.api import rt
   rt.models.contacts.Partner.print_subclasses_graph()


Activities
==========

>>> print(settings.SITE.project_model)
<class 'lino_tera.lib.courses.models.Course'>


.. _tera.specs.teams:

Teams
=====

>>> rt.show(teams.Teams)
=========== ============= ================== ==================
 Reference   Designation   Designation (de)   Designation (fr)
----------- ------------- ------------------ ------------------
 E           Eupen
 S           St. Vith
=========== ============= ================== ==================
<BLANKLINE>


.. _dt.apps.tera.finan.xml:

Write an XML file of a payment order
====================================

The following just repeats on the first payment order what has been
done for all orders when :mod:`lino_xl.lib.finan.fixtures.demo`
generated them:

>>> ses = rt.login()
>>> obj = rt.models.finan.PaymentOrder.objects.first()
>>> obj
PaymentOrder #87 ('PMO 1/2015')

>>> rv = obj.write_xml.run_from_session(ses)  #doctest: +ELLIPSIS
xml render <django.template.backends.jinja2.Template object at ...> -> .../media/xml/xml/PMO-2015-1.xml ('en', {})
Validate .../media/xml/xml/PMO-2015-1.xml against .../lino_xl/lib/finan/XSD/pain.001.001.02.xsd ...


>>> rv['success']
True
>>> print(rv['open_url'])
/media/xml/xml/PMO-2015-1.xml

Let's check whether the XML file has been generated and is a valid
SEPA payment initiation:

>>> fn = settings.SITE.site_dir / rv['open_url'][1:]
>>> fn.exists()
True

>>> from lino_xl.lib.finan.validate import validate_pain001
>>> validate_pain001(str(fn))


Voucher types
=============

>>> rt.show(accounting.VoucherTypes)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
=============================== ====== ================================================================ ========================================================
 value                           name   text                                                             Model
------------------------------- ------ ---------------------------------------------------------------- --------------------------------------------------------
 ana.InvoicesByJournal                  Analytic invoice (ana.InvoicesByJournal)                         <class 'lino_xl.lib.ana.models.AnaAccountInvoice'>
 bevats.DeclarationsByJournal           Special Belgian VAT declaration (bevats.DeclarationsByJournal)   <class 'lino_xl.lib.bevats.models.Declaration'>
 finan.BankStatementsByJournal          Bank statement (finan.BankStatementsByJournal)                   <class 'lino_xl.lib.finan.models.BankStatement'>
 finan.JournalEntriesByJournal          Journal entry (finan.JournalEntriesByJournal)                    <class 'lino_xl.lib.finan.models.JournalEntry'>
 finan.PaymentOrdersByJournal           Payment order (finan.PaymentOrdersByJournal)                     <class 'lino_xl.lib.finan.models.PaymentOrder'>
 trading.InvoicesByJournal              Trading invoice (trading.InvoicesByJournal)                      <class 'lino_xl.lib.trading.models.VatProductInvoice'>
 vat.InvoicesByJournal                  Ledger invoice (vat.InvoicesByJournal)                           <class 'lino_xl.lib.vat.models.VatAccountInvoice'>
=============================== ====== ================================================================ ========================================================
<BLANKLINE>


>>> # rt.show(accounting.Journals, filter=models.Q(must_declare=True))



Internal details
=================


The following shows that :ticket:`1975` is a duplicate of
:ticket:`492`:

>>> a = rt.models.ana.InvoicesByJournal._actions_dict.get('wf1')
>>> a.action.auto_save
True




Technical stuff (don't read)
============================

>>> rt.show("excerpts.ExcerptTypes")
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
============================================================== ========= ============ ==================== ====================== ====================== ===================== ============================= ===============
 Model                                                          Primary   Certifying   Designation          Designation (de)       Designation (fr)       Print method          Template                      Body template
-------------------------------------------------------------- --------- ------------ -------------------- ---------------------- ---------------------- --------------------- ----------------------------- ---------------
 `bevats.Declaration (Special Belgian VAT declaration) <…>`__   Yes       Yes          VAT declaration      MwSt.-Erklärung        VAT declaration        WeasyPdfBuildMethod   default.weasy.html
 `contacts.Partner (Partner) <…>`__                             No        No           Payment reminder     Zahlungserinnerung     Rappel de paiement     WeasyPdfBuildMethod   payment_reminder.weasy.html
 `contacts.Person (Person) <…>`__                               No        No           Terms & conditions   Nutzungsbestimmungen   Conditions générales   AppyPdfBuildMethod    TermsConditions.odt
 `courses.Enrolment (Enrolment) <…>`__                          Yes       Yes          Enrolment            Einschreibung          Inscription
 `finan.BankStatement (Bank statement) <…>`__                   Yes       Yes          Bank statement       Kontoauszug            Extrait de compte
 `finan.JournalEntry (Journal entry) <…>`__                     Yes       Yes          Journal entry        Diverse Buchung        Opération diverse
 `finan.PaymentOrder (Payment order) <…>`__                     Yes       Yes          Payment order        Zahlungsauftrag        Ordre de paiement
 `sheets.Report (Accounting Report) <…>`__                      Yes       Yes          Accounting Report    Buchhaltungsbericht    Accounting Report      WeasyPdfBuildMethod
 `trading.VatProductInvoice (Trading invoice) <…>`__            Yes       Yes          Trading invoice      Handelsrechnung        Trading invoice
============================================================== ========= ============ ==================== ====================== ====================== ===================== ============================= ===============
<BLANKLINE>
