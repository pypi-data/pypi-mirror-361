.. doctest docs/dev/choicelists.rst
.. _dev.choicelists:

===========================
Introduction to choicelists
===========================

A :term:`choicelist` is an ordered in-memory list of *choices*.
Each choice has a *value*, a *text* and optionally a *name*.
The **value** of a choice is what is stored in the database.
The **text** is what the user sees.  It is usually translatable.
The **name** can be used to refer to a given choice from program code.

A choicelist looks like a :term:`database table` to the :term:`end user`, but
actually it exists only in the configuration of the server process and is not
stored in a :term:`database`.

Whenever in *plain Django* you use a `choices` attribute on a database
field, in Lino you probably prefer using a :class:`ChoiceList` instead.

You can use a choicelist for more than filling the :attr:`choices` attribute of
a database field.  You can display a choicelist as a table (using :meth:`show
<lino.core.requests.BaseRequest.show>` in a doctest or by adding it to the main
menu).  You can refer to individual choices programmatically using their
:attr:`name`.  You can subclass the choices and add application logic.


.. currentmodule:: lino.core.choicelists

.. contents::
    :depth: 1
    :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino import startup
>>> startup('lino_book.projects.min9.settings')

>>> from lino.api.doctest import *
>>> from django.utils import translation

Examples
========

For example Lino has a :class:`Weekdays <lino.modlib.system.Weekdays>`
choicelist, which has 7 choices, one for each day of the week. Or the
:class:`Genders <lino.modlib.system.Genders>` choicelist. Both examples are
defined in the :mod:`lino.modlib.system` plugin.


Accessing choicelists
=====================

ChoiceLists are **actors**.
Like every actor, choicelists are **never instantiated**.
They are just the class object itself and as such globally available

You can either import them or use :data:`lino.api.rt.models` to access
them (see :ref:`dev.accessing.plugins` for the difference):

>>> rt.models.system.Weekdays
lino.modlib.system.choicelists.Weekdays

>>> from lino.modlib.system.choicelists import Weekdays
>>> Weekdays
lino.modlib.system.choicelists.Weekdays

>>> Weekdays is rt.models.system.Weekdays
True

>>> from lino.modlib.system.choicelists import Genders
>>> Genders is rt.models.system.Genders
True


You can also write code that dynamically resolves a string of type
```app_label.ListName`` to resolve them:

>>> rt.models.resolve('system.Weekdays') is Weekdays
True


Defining choicelists
====================

Here is how the :class:`lino.modlib.system.Weekdays` choicelist has been
defined::

    class Weekdays(dd.ChoiceList):
        verbose_name = _("Weekday")

    add = Weekdays.add_item
    add('1', _('Monday'), 'monday')
    add('2', _('Tuesday'), 'tuesday')
    ...

Note that :meth:`lino.core.choicelists.ChoiceList.add_item` takes at least 2 and
optionally a third positional argument:

- The first argument (`value`) is used to store this choice in a database.
- The second argument (`text`) is what the user sees. It should be translatable.
- The optional third argument (`names`) is used to install this choice as a class
  attribute on its choicelist.

This is the easiest case.  More complex examples, including choicelists with
extended choices:

- :class:`lino.modlib.users.UserTypes`
- :class:`lino.modlib.printing.BuildMethods`

Accessing individual choices
============================

Each row of a choicelist is a **choice**, more precisely an instance
of :class:`lino.core.choicelists.Choice` or a subclass thereof.

Each choice has a "value", a "text" and (optionally) a "name".

The **value** is what gets stored when this choice is assigned to a
database field. It must be unique because it is the analog of primary
key.

>>> [g.value for g in Genders.objects()]
['M', 'F', 'N']

The **text** is what the user sees.  It is a translatable string,
implemented using Django's i18n machine:

>>> Genders.male.text.__class__  #doctest: +ELLIPSIS
<class 'django.utils.functional....__proxy__'>

Calling :func:`str` of a choice is (usually) the same as calling
:func:`str` on its `text` attribute:

>>> [str(g) for g in Genders.objects()]
['Male', 'Female', 'Nonbinary']

The text of a choice depends on the current user language.

>>> with translation.override('fr'):
...     [str(g) for g in Genders.objects()]
['Masculin', 'Féminin', 'Non binaire']

>>> with translation.override('de'):
...     [str(g) for g in Genders.objects()]
['Männlich', 'Weiblich', 'Nichtbinär']

>>> with translation.override('et'):
...     [str(g) for g in Genders.objects()]
['Mees', 'Naine', 'Mittebinaarne']


The text of a choice is a **translatable** string, while *value* and
*name* remain **unchanged**:

>>> with translation.override('fr'):
...     rt.show('system.Weekdays')
======= =========== ==========
 value   name        text
------- ----------- ----------
 1       monday      Lundi
 2       tuesday     Mardi
 3       wednesday   Mercredi
 4       thursday    Jeudi
 5       friday      Vendredi
 6       saturday    Samedi
 7       sunday      Dimanche
======= =========== ==========
<BLANKLINE>


Named choices
=============

A choice can optionally have a **name**, which makes it accessible as class
attribute on its choicelist so that application code can refer to this
particular choice.

>>> Weekdays.monday
<system.Weekdays.monday:1>

>>> Genders.male
<system.Genders.male:M>

>>> [g.name for g in Genders.objects()]
['male', 'female', 'nonbinary']

>>> [d.name for d in Weekdays.objects()]
['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']


Sorting choicelists
===================

The items of a choicelist are sorted by their order of creation, not by their
value. This is visible e.g. in :class:`lino.modlib.system.DurationUnits`.

Lino displays the choices of a choicelist in a combobox in their natural order
of how they have been added to the list.

You can explicitly call :meth:`Choicelist.sort` to sort them. This makes sense
e.g. in :mod:`lino_presto.lib.accounting` where we add a new journal group "Orders",
which we want to come before any other journal groups.


Choicelist fields
=================

You use the :class:`Weekdays` choicelist in a model definition as
follows::

    from lino.modlib.system.choicelists import Weekdays

    class WeeklyEvent(dd.Model):
        ...
        day_of_week = Weekdays.field(default=Weekdays.monday)

This adds a database field whose value is an instance of
:class:`lino.core.choicelists.Choice`.

ChoiceListField
===============

A choicelist field is similar to a :class:`ForeignKey` field in that it uses a
:doc:`combo box </dev/combo/index>` as widget, but instead of pointing to a
database object it points to a :class:`Choice`.  For the underlying database it
is actually a `CharField` which contains the `value` (not the `name`) of its
choice.

The :class:`lino.mixins.human.Human` mixin uses the :class:`Genders
<lino.modlib.system.choicelists.Genders>` choicelist as follows::

    class Human(Model):
        ...
        gender = Genders.field(blank=True)

Because :class:`lino_xl.lib.contacts.Person` inherits from
:class:`Human`, you can use this when you want to select all men:

>>> Person = rt.models.contacts.Person
>>> list(Person.objects.filter(gender=Genders.male))
... # doctest: +ELLIPSIS
[Person #112 ('Mr Albert Adam'), Person #116 ('Mr Ilja Adam'), Person #15 ('Mr Hans Altenberg'), ...]

Here is a list of all male first names in our contacts database:

>>> sorted({p.first_name for p in Person.objects.filter(gender=Genders.male)})
['Albert', 'Alfons', 'Andreas', 'Bernd', 'Bruno', 'Christian', 'Daniel', 'David', 'Denis', 'Dennis', 'Didier', 'Eberhart', 'Edgar', 'Edgard', 'Emil', 'Erich', 'Erwin', 'Fritz', 'Gregory', 'Guido', 'Hans', 'Henri', 'Hubert', 'Ilja', 'Jan', 'Jean', 'Johann', 'Josef', 'Jérémy', 'Jérôme', 'Karl', 'Kevin', 'Lars', 'Laurent', 'Luc', 'Ludwig', 'Marc', 'Mark', 'Michael', 'Otto', 'Paul', 'Peter', 'Philippe', 'Rik', 'Robin', 'Vincent']

The same for the ladies:

>>> sorted({p.first_name for p in Person.objects.filter(gender=Genders.female)})
['Alice', 'Annette', 'Berta', 'Charlotte', 'Clara', 'Daniela', 'Dora', 'Dorothée', 'Erna', 'Eveline', 'Françoise', 'Gaby', 'Germaine', 'Hedi', 'Hildegard', 'Inge', 'Irene', 'Irma', 'Jacqueline', 'Josefine', 'Laura', 'Line', 'Lisa', 'Marie-Louise', 'Melba', 'Melissa', 'Monique', 'Noémie', 'Odette', 'Pascale', 'Paula', 'Petra', 'Ulrike', 'Õie']

A ChoiceList has an :meth:`get_list_items` method which returns an iterator
over its choices:

>>> print(Genders.get_list_items())
[<system.Genders.male:M>, <system.Genders.female:F>, <system.Genders.nonbinary:N>]

You may have multiple fields pointing to a same choicelist from a model. For
example  here is how the :class:`lino_xl.lib.cv.LanguageKnowledge` model uses
the :class:`lino_xl.lib.cv.HowWell` choicelist::

  from .choicelists import HowWell

  class LanguageKnowledge(dd.Model):
      ...
      spoken = HowWell.field(_("Spoken"), blank=True)
      written = HowWell.field(_("Written"), blank=True)
      spoken_passively = HowWell.field(_("Spoken (passively)"), blank=True)
      written_passively = HowWell.field(_("Written (passively)"), blank=True)


Customizing the choices display
===============================

We said that the **value** of a choice is what is stored in the database, while
the **text** is what the user sees, but there are situations where the end user
wants to see **both** the value and the text.

For such lists you can set :attr:`ChoiceList.show_values` to `True`.

For example
:class:`lino.modlib.users.UserTypes`,
:class:`lino_xl.lib.accounting.CommonAccounts` or
:ref:`VatClasses.be`.


Editing choicelists
===================

While choicelists look "read-only" to end users because they are not editable
via the web front end, they can actually be modified by both the
:term:`application developer` or the local :term:`server administrator`.

Let's use the :class:`lino.modlib.system.Genders` choicelist as an example. It
is defined in the code (file `lino/modlib/system/choicelists.py
<https://gitlab.com/lino-framework/lino/-/blob/master/lino/modlib/system/choicelists.py?ref_type=heads>`__)
as follows::

  class Genders(ChoiceList):
      verbose_name = _("Gender")

  add = Genders.add_item
  add('M', _("Male"), 'male')
  add('F', _("Female"), 'female')
  add('N', _("Nonbinary"), 'nonbinary')

We can show the result:

>>> rt.show(system.Genders)
======= =========== ===========
 value   name        text
------- ----------- -----------
 M       male        Male
 F       female      Female
 N       nonbinary   Nonbinary
======= =========== ===========
<BLANKLINE>

Now let's imagine that the :term:`site operator` (your customer) wants you to
change that list for their particular website.

In a first scenario let's imagine that they want you to remove the nonbinary
choice, i.e. they want only the two traditional choices "male" and "female" in
their database. (We don't discuss about controversial topics with our customers
and this is just a first example, okay?)

As a :term:`server administrator` you would do this in a
:attr:`workflows_module <lino.core.site.Site.workflows_module>` or a
:attr:`user_types_module <lino.core.site.Site.user_types_module>`.

>>> from lino.api import _

We recommend to not delete individual choices but to clear the whole list and
redefine it from scratch.

>>> Genders = system.Genders
>>> Genders.clear()

If you'd look at the list now, you'd get:

>>> rt.show(Genders)
No data to display

>>> add = Genders.add_item
>>> add('M', _("Male"), 'male')
<system.Genders.male:M>
>>> add('F', _("Female"), 'female')
<system.Genders.female:F>

Here is what your first customer wanted to see:

>>> rt.show(Genders)
======= ======== ========
 value   name     text
------- -------- --------
 M       male     Male
 F       female   Female
======= ======== ========
<BLANKLINE>


In a second scenario let's imagine that your customer wants you to *expand* the
nonbinary choice into a list of more specific choices. (Again, we don't discuss
about controversial topics and this is just a second example, okay?)

The `value` must be a string.

>>> Genders.add_item(3, _("Third"), 'third')
Traceback (most recent call last):
...
Exception: value must be a string

Lino protects you from accidentally adding a choice with the same value as an
existing choice.

>>> Genders.add_item("M", _("Macho"), 'macho')
Traceback (most recent call last):
...
Exception: Duplicate value 'M' in system.Genders.

Lino protects you from accidentally giving new choices a name that is already
used.

>>> Genders.add_item("R", _("Really male"), 'male')
Traceback (most recent call last):
...
Exception: An attribute named 'male' is already defined in Genders

Note that certain "names" are used by the :class:`ChoiceList` class.

>>> Genders.add_item("V", _("Verbose name"), 'verbose_name')
Traceback (most recent call last):
...
Exception: An attribute named 'verbose_name' is already defined in Genders

>>> Genders.add_item("L", _("Lesbian"), 'lesbian')
<system.Genders.lesbian:L>

>>> Genders.add_item("G", _("Gay"), 'gay')
<system.Genders.gay:G>

>>> Genders.add_item("B", _("Bisexual"), 'bi')
<system.Genders.bi:B>
>>> Genders.add_item("T", _("Transsexual"), 'trans')
<system.Genders.trans:T>

You may give multiple names (synonyms) to a choice by specifying them as a
space-separated list of names.

>>> Genders.add_item("Q", _("Queer"), 'queer tribade lipstick invert')
<system.Genders.queer:Q>

In that case the first name will be the default name, but the other names refer
to exactly the same choice:

>>> Genders.queer is Genders.tribade
True
>>> Genders.queer is Genders.invert
True

Now you made also your second customer happy:

>>> rt.show(Genders)
======= =============================== =============
 value   name                            text
------- ------------------------------- -------------
 M       male                            Male
 F       female                          Female
 L       lesbian                         Lesbian
 G       gay                             Gay
 B       bi                              Bisexual
 T       trans                           Transsexual
 Q       queer tribade lipstick invert   Queer
======= =============================== =============
<BLANKLINE>



Miscellaneous
=============

Comparing Choices uses their *value* (not the *name* nor *text*):

>>> UserTypes = rt.models.users.UserTypes

>>> UserTypes.admin > UserTypes.user
True
>>> UserTypes.admin == '900'
True
>>> UserTypes.admin == 'manager'
False
>>> UserTypes.admin == ''
False




Seeing all choicelists in your application
==========================================

>>> from lino.core.kernel import choicelist_choices
>>> pprint(choicelist_choices())
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
[('about.DateFormats', 'about.DateFormats (Date formats)'),
 ('about.TimeZones', 'about.TimeZones (Time zones)'),
 ('accounting.CommonAccounts', 'accounting.CommonAccounts (Common accounts)'),
 ('accounting.DC', 'accounting.DC (Booking directions)'),
 ('accounting.JournalGroups', 'accounting.JournalGroups (Journal groups)'),
 ('accounting.TradeTypes', 'accounting.TradeTypes (Trade types)'),
 ('accounting.VoucherStates', 'accounting.VoucherStates (Voucher states)'),
 ('accounting.VoucherTypes', 'accounting.VoucherTypes (Voucher types)'),
 ('addresses.AddressTypes', 'addresses.AddressTypes (Address types)'),
 ('addresses.DataSources', 'addresses.DataSources (Data sources)'),
 ('cal.EntryStates', 'cal.EntryStates (Entry states)'),
 ('cal.EventEvents', 'cal.EventEvents (Observed events)'),
 ('cal.GuestStates', 'cal.GuestStates (Presence states)'),
 ('cal.NotifyBeforeUnits', 'cal.NotifyBeforeUnits (Notify Units)'),
 ('cal.PlannerColumns', 'cal.PlannerColumns (Planner columns)'),
 ('cal.ReservationStates', 'cal.ReservationStates (States)'),
 ('cal.TaskStates', 'cal.TaskStates (Task states)'),
 ('cal.YearMonths', 'cal.YearMonths'),
 ('calview.Planners', 'calview.Planners'),
 ('changes.ChangeTypes', 'changes.ChangeTypes (Change Types)'),
 ('checkdata.Checkers', 'checkdata.Checkers (Data checkers)'),
 ('comments.CommentEvents', 'comments.CommentEvents (Observed events)'),
 ('comments.Emotions', 'comments.Emotions (Emotions)'),
 ('contacts.CivilStates', 'contacts.CivilStates (Civil states)'),
 ('contacts.PartnerEvents', 'contacts.PartnerEvents (Observed events)'),
 ('countries.PlaceTypes', 'countries.PlaceTypes'),
 ('courses.ActivityLayouts', 'courses.ActivityLayouts (Course layouts)'),
 ('courses.CourseStates', 'courses.CourseStates (Activity states)'),
 ('courses.EnrolmentStates', 'courses.EnrolmentStates (Enrolment states)'),
 ('cv.CefLevel', 'cv.CefLevel (CEF levels)'),
 ('cv.EducationEntryStates', 'cv.EducationEntryStates'),
 ('cv.HowWell', 'cv.HowWell'),
 ('excerpts.Shortcuts', 'excerpts.Shortcuts (Excerpt shortcuts)'),
 ('households.MemberDependencies',
  'households.MemberDependencies (Household Member Dependencies)'),
 ('households.MemberRoles', 'households.MemberRoles (Household member roles)'),
 ('humanlinks.LinkTypes', 'humanlinks.LinkTypes (Parency types)'),
 ('linod.LogLevels', 'linod.LogLevels (Logging levels)'),
 ('linod.Procedures', 'linod.Procedures (Background procedures)'),
 ('notes.SpecialTypes', 'notes.SpecialTypes (Special note types)'),
 ('notify.MailModes', 'notify.MailModes (Notification modes)'),
 ('notify.MessageTypes', 'notify.MessageTypes (Message Types)'),
 ('periods.PeriodStates', 'periods.PeriodStates (States)'),
 ('periods.PeriodTypes', 'periods.PeriodTypes (Period types)'),
 ('phones.ContactDetailTypes',
  'phones.ContactDetailTypes (Contact detail types)'),
 ('printing.BuildMethods', 'printing.BuildMethods'),
 ('products.BarcodeDrivers', 'products.BarcodeDrivers (Barcode drivers)'),
 ('products.DeliveryUnits', 'products.DeliveryUnits (Delivery units)'),
 ('products.PriceFactors', 'products.PriceFactors (Price factors)'),
 ('products.ProductTypes', 'products.ProductTypes (Product types)'),
 ('properties.DoYouLike', 'properties.DoYouLike'),
 ('properties.HowWell', 'properties.HowWell'),
 ('properties.PropertyAreas', 'properties.PropertyAreas (Property areas)'),
 ('publisher.PageFillers', 'publisher.PageFillers (Page fillers)'),
 ('publisher.PublishingStates',
  'publisher.PublishingStates (Publishing states)'),
 ('publisher.SpecialPages', 'publisher.SpecialPages (Special pages)'),
 ('system.DisplayColors', 'system.DisplayColors (Display colors)'),
 ('system.DurationUnits', 'system.DurationUnits'),
 ('system.Genders', 'system.Genders (Genders)'),
 ('system.PeriodEvents', 'system.PeriodEvents (Observed events)'),
 ('system.Recurrences', 'system.Recurrences (Recurrences)'),
 ('system.Weekdays', 'system.Weekdays'),
 ('system.YesNo', 'system.YesNo (Yes or no)'),
 ('tickets.TicketEvents', 'tickets.TicketEvents (Observed events)'),
 ('tickets.TicketStates', 'tickets.TicketStates (Ticket states)'),
 ('uploads.Shortcuts', 'uploads.Shortcuts (Upload shortcuts)'),
 ('uploads.UploadAreas', 'uploads.UploadAreas (Upload areas)'),
 ('users.UserTypes', 'users.UserTypes (User types)'),
 ('vat.DeclarationFieldsBase',
  'vat.DeclarationFieldsBase (Declaration fields)'),
 ('vat.VatAreas', 'vat.VatAreas (VAT areas)'),
 ('vat.VatClasses', 'vat.VatClasses (VAT classes)'),
 ('vat.VatColumns', 'vat.VatColumns (VAT columns)'),
 ('vat.VatRegimes', 'vat.VatRegimes (VAT regimes)'),
 ('vat.VatRules', 'vat.VatRules (VAT rules)'),
 ('xl.Priorities', 'xl.Priorities (Priorities)')]


The :attr:`lino_xl.lib.properties.PropType.choicelist` field uses this function
for its choices.


Abstract choicelists
====================

.. glossary::

  abstract choicelist

    When you set the :attr:`abstract <lino.core.actors.Actor.abstract>` attribute
    of a choicelist to `True`,  then you can use it like any other choicelist, but
    it becomes invisible for the :term:`front end`.

    Only example so far was :class:`lino.modlib.uploads.Previewers`, which was
    later replaced by the plugin attributes
    :attr:`lino.modlib.uploads.Plugin.full` and
    :attr:`lino.modlib.uploads.Plugin.small`
