.. doctest docs/specs/system.rst
.. _specs.system:

======================================
``system`` : Site-wide system settings
======================================

.. currentmodule:: lino.modlib.system

The :mod:`lino.modlib.system` plugin defines some system features that are
automatically installed with every Lino application.

It especially provides the :class:`SiteConfig` model.


.. contents::
   :depth: 1
   :local:

.. include:: /../docs/shared/include/tested.rst

>>> import lino
>>> lino.startup('lino_book.projects.min9.settings')
>>> from lino.api.doctest import *



Editable site parameters
========================

Lino provides a standard method for defining persistent site parameters that are
editable by :term:`end users <end user>` (at least for those who have access
permission).

.. class:: Dashboard

  This is your :term:`main page`.

.. class:: SiteConfig

    A singleton database object used to store persistent site parameters.

    This model has exactly one instance, which is accessible as the
    :attr:`settings.SITE.site_config <lino.core.site.Site.site_config>`
    property.

    .. attribute:: default_build_method

        The default build method to use when rendering printable documents.

        If this field is empty, Lino uses the value found in
        :attr:`lino.core.site.Site.default_build_method`.

    .. attribute:: simulate_today

        A constant user-defined date to be substituted as current
        system date.

        This should be empty except in situations such as *a
        posteriori* data entry in a prototype.

    .. attribute:: site_company

        The :term:`site operator`, i.e. the legal person that operates this
        :term:`Lino site`.

        See :ref:`ug.site_company`.

        If no plugin named 'contacts' is installed, then this is a
        dummy field and always contains `None`.

    .. attribute:: hide_events_before

        If this is not empty, any calendar events before that date are
        being hidden in certain places.

        For example OverdueEvents, EntriesByController, ...

        Injected by :mod:`lino_xl.lib.cal`.

.. class:: SiteConfigManager

    Returns the cached instance, which holds the one and only database instance.

.. class:: Lockable

    Mixin to add row-level edit locking to any model.

    Models with row-level edit locking are not editable in detail view
    by default.  All form fields are disabled. The user must click
    :guilabel:`Edit` in order to request an edit lock for that row.
    This will enable all fields (except those which are disabled for
    some other reason).

    Caveats: locking a row and then navigating away without changing
    anything will leave the row locked.


.. class:: BuildSiteCache

    Rebuild the site cache.
    This action is available on :class:`About`.


.. class:: SiteConfigs

    The table used to present the :class:`SiteConfig` row in a Detail form.

    See also :meth:`lino.core.site.Site.get_site_config`.


Recurrences in the system
==========================


.. class:: RecurrenceSet

    Mixin for :term:`database models <database model>` that express a set of
    repeating ("recurrent") events. Example usage can be found in
    :ref:`specs.cal.automatic_events`.

    .. attribute:: start_date

        The start date of the first meeting to be generated.

    .. attribute:: end_date

        The end date of the first meeting to be generated.  Leave
        this field empty if the meetings last less than one day.

    .. attribute:: start_time
    .. attribute:: end_time

    .. attribute:: every

        The frequency of periodic iteration: daily, weekly, monthly or yearly.

    .. attribute:: every_unit

        The interval between each periodic iteration.

        For example, when :attr:`every` is yearly, an :attr:`every_unit` of 2
        means once every two years. The default value is 1.

    .. attribute:: positions

        Space-separated list of one or several positions within the recurrency
        cycle.

        Each position is a positive or negative integer expressing which
        occurrence is to be taken from the recurrency period. For example if
        :attr:`positions` is `-1` and :attr:`every_unit` is monthly, we get the
        last day of every month.

        Inspired by `dateutil.rrule <https://dateutil.readthedocs.io/en/stable/rrule.html>`_.

    .. attribute:: max_events

        Maximum number of calendar entries to generate.

    .. attribute:: monday
    .. attribute:: tuesday
    .. attribute:: wednesday
    .. attribute:: thursday
    .. attribute:: friday
    .. attribute:: saturday
    .. attribute:: sunday


    .. attribute:: weekdays_text

        A virtual field returning the textual formulation of the
        weekdays where the recurrence occurs.

        Usage examples see :ref:`book.specs.cal`.


.. class:: Recurrences

    List of possible choices for a 'recurrency' field.

    A recurrency (an item of this choicelist) is also a :class:`DurationUnit`.

    .. attribute:: easter

        Repeat events yearly, moving them together with the Easter
        data of that year.

        Lino computes the offset (number of days) between this rule's
        :attr:`start_date` and the Easter date of that year, and
        generates subsequent events so that this offset remains the
        same.


The days of the week
=====================

.. class:: Weekdays

    A choicelist with the seven days of a week.

The available values in the system are.

>>> rt.show(system.Weekdays)
======= =========== ===========
 value   name        text
------- ----------- -----------
 1       monday      Monday
 2       tuesday     Tuesday
 3       wednesday   Wednesday
 4       thursday    Thursday
 5       friday      Friday
 6       saturday    Saturday
 7       sunday      Sunday
======= =========== ===========
<BLANKLINE>


.. data:: WORKDAYS

    The five workdays of the week (Monday to Friday).


Duration units
==============

The system plugin defines :class:`DurationUnits` choicelist, a
site-wide list of **duration units**.


.. class:: DurationUnits

    The list of possible duration units defined by this application.

    This is used as the selection list for the :attr:`duration_unit
    <lino_xl.lib.cal.Event.duration_unit>` field of a :term:`calendar entry`.

    Every item is an instance of :class:`DurationUnit`.


.. class:: DurationUnit

    Base class for the choices in the :class:`DurationUnits` choicelist.

    .. method:: add_duration(unit, orig, value)

        Return a date or datetime obtained by adding `value`
        times this `unit` to the specified value `orig`.
        Returns None is `orig` is empty.

        This is intended for use as a `curried magic method` of a
        specified list item:

The available values in the system are:

>>> rt.show(system.DurationUnits)
======= ========= =========
 value   name      text
------- --------- ---------
 s       seconds   seconds
 m       minutes   minutes
 h       hours     hours
 D       days      days
 W       weeks     weeks
 M       months    months
 Y       years     years
======= ========= =========
<BLANKLINE>

Duration units can be used for arithmetic operation on durations. For
example:

>>> from lino.modlib.system.choicelists import DurationUnits
>>> start_date = i2d(20111026)
>>> DurationUnits.months.add_duration(start_date, 2)
datetime.date(2011, 12, 26)

>>> from lino.utils import i2d
>>> start_date = i2d(20111026)
>>> DurationUnits.months.add_duration(start_date, 2)
datetime.date(2011, 12, 26)
>>> DurationUnits.months.add_duration(start_date, -2)
datetime.date(2011, 8, 26)

>>> start_date = i2d(20110131)
>>> DurationUnits.months.add_duration(start_date, 1)
datetime.date(2011, 2, 28)
>>> DurationUnits.months.add_duration(start_date, -1)
datetime.date(2010, 12, 31)
>>> DurationUnits.months.add_duration(start_date, -2)
datetime.date(2010, 11, 30)

>>> start_date = i2d(20140401)
>>> DurationUnits.months.add_duration(start_date, 3)
datetime.date(2014, 7, 1)
>>> DurationUnits.years.add_duration(start_date, 1)
datetime.date(2015, 4, 1)


Display colors
==============

.. class:: DisplayColors

    A list of colors to be specified for displaying.

This is a subset of the `140 colors supported by all modern browsers
<https://www.w3schools.com/tags/ref_colornames.asp>`__

>>> rt.show(system.DisplayColors)
======= ============ ============ ============
 value   name         text         Font color
------- ------------ ------------ ------------
 100     white        White        black
 110     gray         Gray         black
 120     black        Black        white
 210     red          Red          white
 220     orange       Orange       white
 230     yellow       Yellow       black
 240     green        Green        white
 250     blue         Blue         white
 260     magenta      Magenta      white
 270     violet       Violet       white
 300     silver       Silver       black
 310     maroon       Maroon       white
 311     peru         Peru         white
 312     pink         Pink         black
 320     olive        Olive        white
 330     aqua         Aqua         white
 340     navy         Navy         white
 341     aquamarine   Aquamarine   black
 342     darkgreen    DarkGreen    white
 343     palegreen    PaleGreen    black
 344     chartreuse   Chartreuse   black
 345     lime         Lime         black
 346     teal         Teal         white
 350     fuchsia      Fuchsia      white
 351     cyan         Cyan         black
 361     purple       Purple       white
======= ============ ============ ============
<BLANKLINE>

Here is how these colors are rendered in your browser:

.. py2rst::

  from lino.api.shell import *
  print(".. raw:: html\n")
  for dc in system.DisplayColors.get_list_items():
       print(f"""  <span style="background-color:{dc.name};color:{dc.font_color}">&nbsp;{dc.text}&nbsp;</span>""")


Miscellaneous
=============


.. class:: BleachChecker

    A data checker used to find unbleached html content.


.. class:: Genders

    Defines the possible choices for the gender of a person ("male", "female"
    and "nonbinary").

    >>> rt.show('system.Genders')
    ======= =========== ===========
     value   name        text
    ------- ----------- -----------
     M       male        Male
     F       female      Female
     N       nonbinary   Nonbinary
    ======= =========== ===========
    <BLANKLINE>

    This :term:`choicelist` is used for deciding the salutation (Mr/Mrs) and for
    its :meth:`mf` method. See :ref:`lino.tutorial.human`.


.. class:: YesNo

    A choicelist with two values "Yes" and "No".

    Used e.g. to define parameter panel fields for BooleanFields::

      foo = dd.YesNo.field(_("Foo"), blank=True)

.. class:: ObservedEvent

    Base class for choices of "observed event"-style choicelists.

    .. method:: add_filter(self, qs, pv)

        Add a filter to the given Django queryset. The given `obj` must be
        either a `datetime.date` object or must have two attributes
        `start_date` and `end_date`. The easiest way is to have it an
        instance of :class:`DateRange
        <lino.mixins.periods.DateRange>` or :class:`DateRangeValue
        <lino.utils.dates.DateRangeValue>`.




.. class:: PeriodEvents

    The list of things you can observe on a
    :class:`lino.mixins.periods.DateRange`.


.. class:: TimeZones

  Used by :attr:`lino.modlib.users.User.time_zone` and
  :attr:`lino_xl.lib.working.Session.time_zone`.

  See also :setting:`USE_TZ`.

.. class:: DateFormats

  Used by :attr:`lino.modlib.users.User.date_format`.
