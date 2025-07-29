.. doctest docs/plugins/contacts.rst
.. include:: /../docs/shared/include/defs.rst
.. _specs.contacts:

================================
``contacts`` : Managing contacts
================================

.. currentmodule:: lino_xl.lib.contacts

The :mod:`lino_xl.lib.contacts` plugin adds functionality for managing contacts.
It adds the concepts of :term:`partner`, :term:`person`, :term:`organization` and "contact
roles".

We assume you have read the :ref:`ug.plugins.contacts` page of the :ref:`ug`.


.. contents::
   :depth: 1
   :local:

.. include:: /../docs/shared/include/tested.rst

>>> import lino
>>> lino.startup('lino_book.projects.min9.settings')
>>> from django.utils import translation
>>> from lino.api.doctest import *
>>> from django.db.models import Q

Database structure
==================

The main models are :class:`Person` and :class:`Company` and their
common base :class:`Partner`.

A :class:`RoleType` ("Function") where you can configure the available
functions. TODO: rename "RoleType" to "Function" or "ContactType"?

A :class:`CompanyType` model can be used to classify :term:`organizations <organization>`.



Multi-table inheritance
=======================

The contacts plugin defines two subclasses of :class:`Partner`: :class:`Person`
and :class:`Company`. Applications can define other subclasses for
:class:`Partner`.

The :class:`Partner` model is *not abstract*, i.e. you can see a table where
persons and organizations are together.  This is useful e.g. in accounting
reports where all partners are handled equally, without making a difference
between natural an legal persons.


Menu entries
============

This plugin adds the following menu entries:

- :menuselection:`Contacts --> Persons`
- :menuselection:`Contacts --> Organizations`

- :menuselection:`Configuration --> Contacts --> Functions`
- :menuselection:`Configuration --> Contacts --> Organization types`

- :menuselection:`Explorer --> Contacts --> Partners`
- :menuselection:`Explorer --> Contacts --> Contact persons`


>>> show_menu_path('contacts.Persons')
Contacts --> Persons
>>> show_menu_path('contacts.Companies')
Contacts --> Organizations
>>> show_menu_path('contacts.Partners')
Explorer --> Contacts --> Partners



Dependencies
============

This plugin needs :mod:`lino_xl.lib.countries` and :mod:`lino.modlib.system`.

This plugin is being extended by :ref:`welfare` in
:mod:`lino_welfare.modlib.contacts` or by :ref:`voga` in
:mod:`lino_voga.modlib.contacts`.

Contact functions
=================

The demo database defines the following :term:`contact functions <contact
function>`:

>>> rt.show(contacts.RoleTypes)
==== ============= ================== ===================== ====================
 ID   Designation   Designation (de)   Designation (fr)      Authorized to sign
---- ------------- ------------------ --------------------- --------------------
 1    CEO           Geschäftsführer    Gérant                Yes
 2    Director      Direktor           Directeur             Yes
 3    Secretary     Sekretär           Secrétaire            No
 4    IT manager    EDV-Manager        Gérant informatique   No
 5    President     Präsident          Président             Yes
==== ============= ================== ===================== ====================
<BLANKLINE>


Contact roles
=============

Any given person can play a role in one or multiple companies.

>>> ses = rt.login("robin")
>>> ses.show(contacts.Roles)
==== ========== ==================== =====================
 ID   Function   Person               Organization
---- ---------- -------------------- ---------------------
 1    CEO        Mrs Annette Arens    Bäckerei Ausdemwald
 2    CEO        Mrs Erna Ärgerlich   Garage Mergelsberg
 3    CEO        Mrs Erna Ärgerlich   Rumma & Ko OÜ
==== ========== ==================== =====================
<BLANKLINE>

The :meth:`__str__` method of :class:`Role` summarizes the meaning of every
:term:`database row`:

>>> for obj in contacts.Roles.request():
...     print(obj)
Mrs Annette Arens is CEO at Bäckerei Ausdemwald
Mrs Erna Ärgerlich is CEO at Garage Mergelsberg
Mrs Erna Ärgerlich is CEO at Rumma & Ko OÜ

If we look at the roles within a company, Lino shows only the person and the
function because :attr:`Roles.company` is an :term:`obvious field`.

>>> company = contacts.Company.objects.get(name="Garage Mergelsberg")
>>> person = contacts.Person.objects.get(last_name="Ärgerlich")
>>> ses.show(contacts.RolesByCompany, company)
`Mrs Erna Ärgerlich (CEO) <…>`__, **New**

The same applies when we look at the roles by person. No need to repeat the person for each role because
:attr:`Role.person` is an :term:`obvious field`

>>> ses.show(contacts.RolesByPerson, person)
`Garage Mergelsberg (CEO) <…>`__, `Rumma & Ko OÜ (CEO) <…>`__, **New**


The site operator
=================

When this plugin is installed, the :term:`site manager` usually creates a
:class:`Company` that represents the :term:`site operator`, and have the field
:attr:`SiteConfig.site_company` point to it (as explained in
:ref:`ug.site_company`).

>>> siteop = settings.SITE.plugins.contacts.site_owner
>>> siteop.__class__.__name__
'Company'

>>> print(siteop)
Rumma & Ko OÜ

>>> for obj in siteop.get_signers():
...     print("{}, {}".format(obj.person.get_full_name(), obj.type))
Mrs Erna Ärgerlich, CEO



Models and views
================

.. class:: Partner

    The :term:`database model` used to represent a :term:`business partner`.

    .. attribute:: name

        The full name of this partner.

        Subclasses may hide this field and fill it automatically. For example on
        a :class:`Person`, Lino automatically sets the :attr:`name` field to
        `<last_name>, <first_name>`, and the field is usually hidden for end
        users. Even when hidden, it can be used for alphabetic sorting.

    .. attribute:: prefix

        An optional name prefix. For organisations this is inserted
        before the name, for persons this is inserted between first
        name and last name.

        See :meth:`lino.mixins.human.Human.get_last_name_prefix`.

    .. attribute:: email

        The primary email address.

    .. attribute:: phone

        The primary phone number.

        Note that Lino does not ignore formatting characters in phone numbers
        when searching.  For example, if you enter "087/12.34.56" as a phone
        number, then a search for phone number containing "1234" will *not*
        find it.

    .. attribute:: gsm

        The primary mobile phone number.

    .. attribute:: language

        The language to use when communicating with this partner.

    .. attribute:: purchase_account

        The general account to suggest as default value in purchase
        invoices from this partner.

        This field exists only when :mod:`lino_xl.lib.accounting` is installed,
        which uses it as the :attr:`invoice_account_field_name
        <lino_xl.lib.accounting.TradeType.invoice_account_field_name>` for
        :attr:`TradeTypes.purchases <lino_xl.lib.accounting.TradeTypes.purchases>`.

    Two fields exist only when :mod:`lino_xl.lib.vat` is installed:

    .. attribute:: vat_regime

        The default VAT regime to use on invoices for this partner.

    .. attribute:: vat_id

        The national VAT identification number of this partner.

    .. attribute:: partner_ref

        How this partner refers to us.


.. class:: Partners

  .. attribute:: detail_layout

      The :term:`detail layout` of the Partners table is not set by default.
      Especially accounting applications will set it to ``'contacts.PartnerDetail'``.

      That's because the Partners view that shows companies and persons merged
      together is useful only for certain accounting reports.


.. class:: Person

    The :term:`database model` used to represent a :term:`person`.

    .. attribute:: first_name
    .. attribute:: last_name
    .. attribute:: gender

    .. attribute:: name

      See :attr:`Partner.name`.



.. class:: Persons

    Shows all persons.


.. class:: Company

    The :term:`database model` used to represent an :term:`organization`.

    The verbose name is "Organization" while the internal name is "Company" for
    historical reasons and because that's easier to type.

    Inherits from :class:`Partner`.

    .. attribute:: type

        Pointer to the :class:`CompanyType`.

    .. method:: get_signers(today=None)

        Return an iterable over the :term:`contact persons <contact person>` who
        can sign business documents (i.e. exercise a :term:`signer function`)
        for this organization.

        If `today` is specified and :attr:`with_roles_history
        <lino_xl.lib.contacts.Plugin.with_roles_history>` is `True`, return only
        the contact persons that were exercising a :term:`signer function` at
        the given date.

        :term:`contact person` represents
        a person that signs contracts, invoices or other business documents for the
        :term:`site operator`.


.. class:: Companies

  Base table for all tables on  :term:`organizations <organization>`.


.. class:: Role

    The :term:`database model` used to represent a :term:`contact person`.

    .. attribute:: company

        The organization where this person has this role.

    .. attribute:: type

        The function of this person in this organization.

    .. attribute:: person

        The person having this role in this organization.

        This is a learning foreign key. See `Automatically creating contact persons`_

    .. attribute:: start_date

        When this person started to exercise this function in this
        organization.

        This is a dummy field when :attr:`Plugin.with_roles_history`
        is `False`.

    .. attribute:: end_date

        When this person stopped to exercise this function in this
        organization.

        This is a dummy field when :attr:`Plugin.with_roles_history`
        is `False`.

.. class:: RoleType

    The :term:`database model` used to represent a :term:`contact function`.

    .. attribute:: name

        A translatable designation. Used e.g. in document templates
        for contracts.

    .. attribute:: can_sign

        Whether this is a :term:`signer function`.


.. class:: PartnerRelated

  Abstract model mixin for things that are related to one and only one
  :term:`partner`.

  .. attribute:: partner

      The recipient of this document.  This can be a :term:`person`, an
      :term:`organization` or any type of :term:`business partner`.

      A pointer to :class:`lino_xl.lib.contacts.Partner`.

  .. attribute:: recipient

      Alias for the partner



Quick search
============

About the :term:`quick search field` in contacts.

When doing a quick search in a list of partners, Lino searches only the
:attr:`name <Partner.name>` field and not the street.

>>> rt.show(contacts.Partners, quick_search="berg")
==================== ==== ====================================== ================
 Name                 ID   See as                                 e-mail address
-------------------- ---- -------------------------------------- ----------------
 Altenberg Hans       15   Organization, **Partner**, Household
 Garage Mergelsberg   5    **Partner**, Person, Household
==================== ==== ====================================== ================
<BLANKLINE>

Without that restriction, a user who enters "berg" in the quick search
field would also get e.g. the following partners (because their
address contains the query string):

>>> rt.show(contacts.Partners, column_names="name street",
...     filter=Q(street__icontains="berg"))
===================== ===================
 Name                  Street
--------------------- -------------------
 Bastiaensen Laurent   Am Berg
 Collard Charlotte     Auf dem Spitzberg
 Ernst Berta           Bergkapellstraße
 Evers Eberhart        Bergstraße
 Kaivers Karl          Haasberg
 Lazarus Line          Heidberg
===================== ===================
<BLANKLINE>

This behaviour is implemented using the :attr:`quick_search_fields
<lino.core.model.Model.quick_search_fields>` attribute on the model.

>>> contacts.Partner.quick_search_fields
(<django.db.models.fields.CharField: prefix>, <django.db.models.fields.CharField: name>, <django.db.models.fields.CharField: phone>, <django.db.models.fields.CharField: gsm>)


Numeric quick search
====================

You can search for phone numbers

>>> rt.show(contacts.Partners, quick_search="123", column_names="name phone id")
=============== ============== =====
 Name            Phone          ID
--------------- -------------- -----
 Adam Pascale                   123
 Arens Andreas   +32 87123456   13
 Arens Annette   +32 87123457   14
=============== ============== =====
<BLANKLINE>


When the search string starts with "#", the user wants to get the partner with
that primary key.

>>> rt.show(contacts.Partners, quick_search="#12", column_names="name phone id")
================== ======= ====
 Name               Phone   ID
------------------ ------- ----
 Auto École Verte           12
================== ======= ====
<BLANKLINE>

This behaviour is the same for all subclasses of Partner, e.g. for
persons and for organizations.


>>> rt.show(contacts.Persons, quick_search="berg")
=================== ============================= ================ ======= ======== ==== ==========
 Name                Address                       e-mail address   Phone   Mobile   ID   Language
------------------- ----------------------------- ---------------- ------- -------- ---- ----------
 Mr Hans Altenberg   Aachener Straße, 4700 Eupen                                     15
=================== ============================= ================ ======= ======== ==== ==========
<BLANKLINE>

>>> rt.show(contacts.Companies, quick_search="berg")
==================== ============================= ================ ======= ======== ==== ==========
 Name                 Address                       e-mail address   Phone   Mobile   ID   Language
-------------------- ----------------------------- ---------------- ------- -------- ---- ----------
 Garage Mergelsberg   Hauptstraße 13, 4730 Raeren                                     5
==================== ============================= ================ ======= ======== ==== ==========
<BLANKLINE>



Exporting contacts as vcard files
=================================

.. class:: ExportVCardFile

    Download all records as a .vcf file which you can import to another
    contacts application.

    This action exists on every list of partners when your
    application has :attr:`use_vcard_export
    <lino_xl.lib.contacts.Plugin.use_vcard_export>` set to `True`.



User roles
==========

.. class:: SimpleContactsUser

   A user who has access to basic contacts functionality.

.. class:: ContactsUser

   A user who has access to full contacts functionality.

.. class:: ContactsStaff

   A user who can configure contacts functionality.

Filtering partners
==================

.. class:: PartnerEvents

    A choicelist of observable partner events.

    .. attribute:: has_open_movements

      See :ref:`has_open_movements` in :ref:`xl.specs.accounting`.
      This choice exists only when :mod:`lino_xl.lib.accounting` is installed.

Other models
============

.. class:: CompanyTypes
.. class:: CompanyType

    A type of organization. Used by :attr:`Company.type` field.


Model mixins
============

.. class:: ContactRelated

    Model mixin for things that relate to **either** a private person
    **or** a company, the latter potentially represented by a contact
    person having a given role in that company.  Typical usages are
    **invoices** or **contracts**.

    Adds 3 database fields and two virtual fields.

    .. attribute:: company

        Pointer to :class:`Company`.

    .. attribute:: contact_person

        Pointer to :class:`Person`.

    .. attribute:: contact_role

        The optional :class:`Role`
        of the :attr:`contact_person` within :attr:`company`.

    .. attribute:: partner

        (Virtual field) The "legal partner", i.e. usually the
        :attr:`company`, except when that field is empty, in which
        case `partner` contains the :attr:`contact_person`.  If both
        fields are empty, then `partner` contains `None`.

    .. attribute:: recipient

        (Virtual field) The :class:`Addressable
        <lino.utils.addressable.Addressable>` object to use when
        printing a postal address for this.
        This is typically either the :attr:`company` or
        :attr:`contact_person` (if one of these fields is
        non-empty). It may also be a
        :class:`lino_xl.lib.contacts.models.Role` object.


    Difference between :attr:`partner` and `recipient`: an invoice can
    be issued and addressed to a given person in a company (i.e. a
    :class:`Role <lino_xl.lib.contacts.models.Role>` object), but
    accountants want to know the juristic person, which is either the
    :attr:`company` or a private :attr:`person` (if no :attr:`company`
    specified), but not a combination of both.


.. class:: PartnerDocument

    Deprecated.
    Adds two fields 'partner' and 'person' to this model, making it
    something that refers to a "partner".  `person` means a "contact
    person" for the partner.



Print templates
===============


.. xfile:: contacts/Person/TermsConditions.odt

    Prints a "Terms & Conditions" document to be used by organisations
    who need a signed permission from their clients for storing their
    contact data.  The default content may be localized.


Civil state
===========

>>> show_choicelist(contacts.CivilStates)
======= ==================== ==================== ============================= =============================
 value   name                 en                   de                            fr
------- -------------------- -------------------- ----------------------------- -----------------------------
 10      single               Single               Ledig                         célibataire
 20      married              Married              Verheiratet                   marié
 30      widowed              Widowed              Verwitwet                     veuf/veuve
 40      divorced             Divorced             Geschieden                    divorcé
 50      separated            Separated            Getrennt von Tisch und Bett   Séparé de corps et de biens
 51      separated_de_facto   De facto separated   Faktisch getrennt             Séparé de fait
 60      cohabitating         Cohabitating         Zusammenwohnend               Cohabitant
======= ==================== ==================== ============================= =============================
<BLANKLINE>


.. class:: CivilStates

    The global list of **civil states** that a person can have.  The
    field pointing to this list is usually named :attr:`civil_state`.

    Usage examples are
    :class:`lino_welfare.modlib.pcsw.models.Client>` and
    :class:`lino_tera.lib.tera.Client>` and
    :class:`lino_avanti.lib.avanti.Client>` .

    **The four official civil states** according to Belgian law are:

    .. attribute:: single

        célibataire : vous n’avez pas de partenaire auquel vous êtes
        officiellement lié

    .. attribute:: married

        marié(e) : vous êtes légalement marié

    .. attribute:: widowed

        veuf (veuve) / Verwitwet : vous êtes légalement marié mais
        votre partenaire est décédé

    .. attribute:: divorced

        divorcé(e) (Geschieden) : votre mariage a été juridiquement dissolu

    **Some institutions define additional civil states** for people
    who are officially still married but at different degrees of
    separation:

    .. attribute:: de_facto_separated

        De facto separated (Séparé de fait, faktisch getrennt)

        Des conjoints sont séparés de fait lorsqu'ils ne respectent
        plus le devoir de cohabitation. Leur mariage n'est cependant
        pas dissous.

        La notion de séparation de fait n'est pas définie par la
        loi. Toutefois, le droit en tient compte dans différents
        domaines, par exemple en matière fiscale ou en matière de
        sécurité sociale (assurance maladie invalidité, allocations
        familiales, chômage, pension, accidents du travail, maladies
        professionnelles).

    .. attribute:: separated

        Legally separated, aka "Separated as to property" (Séparé de
        corps et de biens, Getrennt von Tisch und Bett)

        La séparation de corps et de biens est une procédure
        judiciaire qui, sans dissoudre le mariage, réduit les droits
        et devoirs réciproques des conjoints.  Le devoir de
        cohabitation est supprimé.  Les biens sont séparés.  Les
        impôts sont perçus de la même manière que dans le cas d'un
        divorce. Cette procédure est devenue très rare.

    **Another unofficial civil state** (but relevant in certain
    situations) is:

    .. attribute:: cohabitating

        Cohabitating (cohabitant, zusammenlebend)

        Vous habitez avec votre partenaire et c'est reconnu légalement.

    Sources for above: `belgium.be
    <https://www.belgium.be/fr/famille/couple/divorce_et_separation/separation_de_fait>`__,
    `wikipedia.org <https://en.wikipedia.org/wiki/Cohabitation>`__



.. _specs.contacts.learningfk:

Automatically creating contact persons
======================================

Some examples of how the name is parsed when Lino automatically creates a
:attr:`lino_xl.contacts.Role.person`:

>>> ar = rt.login("robin")

>>> pprint(contacts.Person.choice_text_to_dict("joe smith", ar))
{'first_name': 'Joe', 'last_name': 'Smith'}

>>> pprint(contacts.Person.choice_text_to_dict("Joe W. Smith", ar))
{'first_name': 'Joe W.', 'last_name': 'Smith'}

>>> pprint(contacts.Person.choice_text_to_dict("Joe", ar))
Traceback (most recent call last):
...
django.core.exceptions.ValidationError: ['Cannot find first and last name in "Joe"']

>>> pprint(contacts.Person.choice_text_to_dict("Guido van Rossum", ar))
{'first_name': 'Guido', 'last_name': 'van Rossum'}

The algorithm has already some basic intelligence but plenty of growing potential...

Changing the names of demo persons
==================================

.. management_command:: garble_persons

Garbles person names in an existing database so that it may be used for a demo.

Utilities
=========

:func:`street2kw` to separates house number and optional flat number from street

Examples:

>>> from lino_xl.lib.contacts.utils import street2kw
>>> pprint(street2kw("Limburger Weg"))
{'street': 'Limburger Weg'}
>>> pprint(street2kw("Loten 3"))
{'street': 'Loten', 'street_box': '', 'street_no': '3'}
>>> pprint(street2kw("Loten 3A"))
{'street': 'Loten', 'street_box': 'A', 'street_no': '3'}

>>> pprint(street2kw("In den Loten 3A"))
{'street': 'In den Loten', 'street_box': 'A', 'street_no': '3'}

>>> pprint(street2kw("Auf'm Bach"))
{'street': "Auf'm Bach"}
>>> pprint(street2kw("Auf'm Bach 3"))
{'street': "Auf'm Bach", 'street_box': '', 'street_no': '3'}
>>> pprint(street2kw("Auf'm Bach 3a"))
{'street': "Auf'm Bach", 'street_box': 'a', 'street_no': '3'}
>>> pprint(street2kw("Auf'm Bach 3 A"))
{'street': "Auf'm Bach", 'street_box': 'A', 'street_no': '3'}

Some rather special cases:

>>> pprint(street2kw("rue des 600 Franchimontois 1"))
{'street': 'rue des 600 Franchimontois', 'street_box': '', 'street_no': '1'}

>>> pprint(street2kw("Eupener Strasse 321 /A"))
{'street': 'Eupener Strasse', 'street_box': '/A', 'street_no': '321'}

>>> pprint(street2kw("Neustr. 1 (Referenzadr.)"))
{'addr2': '(Referenzadr.)', 'street': 'Neustr.', 'street_no': '1'}

Edge cases:

>>> street2kw("")
{}

Showing birthdays
=================

When :setting:`contacts.show_birthdays` is `True`, Lino shows the name of
persons who have their birthday today, will have it soon or had it recently.


.. setting:: contacts.show_birthdays

  Whether to show upcoming and recent birthdays as a :term:`welcome message` in
  the dashboard.

  The default value is `True` unless the :term:`application developer` changed
  it.


>>> print("\n".join(contacts.show_birthdays(ar, i2d(20230619))))
<p><b>Birthdays today</b>: <a href="…">Paul Frisch</a> (56), <a href="…">Peter Frisch</a> (36), <a href="…">Clara Frisch</a> (24)</p>

>>> print("\n".join(contacts.show_birthdays(ar, i2d(20231230))))
<p>Recent birthdays: 12-29 <a href="…">Dora Drosson</a> (52)</p>
<p>Upcoming birthdays: 01-01 <a href="…">Philippe Frisch</a> (26), 12-31 <a href="…">Petra Zweith</a> (55)</p>

>>> print("\n".join(contacts.show_birthdays(ar, i2d(20231229))))
<p><b>Birthdays today</b>: <a href="…">Dora Drosson</a> (52)</p>
<p>Upcoming birthdays: 01-01 <a href="…">Philippe Frisch</a> (26), 12-31 <a href="…">Petra Zweith</a> (55)</p>

>>> print("\n".join(contacts.show_birthdays(ar, i2d(20240101))))
<p><b>Birthdays today</b>: <a href="…">Philippe Frisch</a> (27)</p>
<p>Recent birthdays: 12-29 <a href="…">Dora Drosson</a> (53), 12-31 <a href="…">Petra Zweith</a> (56)</p>
<p>Upcoming birthdays: 01-03 <a href="…">Dennis Frisch</a> (23)</p>





Don't read this
===============

>>> def show_help_text(a):
...   print(a.help_text)
...   with translation.override('de'):
...     print(a.help_text)

>>> lst = [contacts.Persons.insert_action,
...   contacts.Companies.insert_action]
>>> for a in lst: show_help_text(a)
Insert a new Person.
Neue(n/s) Person erstellen.
Insert a new Organization.
Neue(n/s) Organisation erstellen.
