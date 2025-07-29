.. doctest docs/topics/datetime.rst

===========================
Manipulating dates and time
===========================


.. contents::
   :depth: 1
   :local:

.. currentmodule:: lino.utils

Import and setup execution context for demonstration purposes.

>>> from lino import startup
>>> startup('lino.projects.std.settings_test')
>>> from lino.utils import *
>>> from django.conf import settings

Covered modules
===============

The following modules define classes related to dates and date ranges. Also
miscellaneous date formatting functions.

- :mod:`lino.utils.dates` contains functionality that doesn't require Django.

- :mod:`lino.utils.date_format` require Django and works only when a
  :envvar:`DJANGO_SETTINGS_MODULE` is defined.


Setting an offset
=================

The following are some usage examples of :func:`date_offset` used on a reference
date given a number of days to offset it:

>>> r = i2d(20140222)

In 10 days:

>>> date_offset(r, 10)
datetime.date(2014, 3, 4)

Four hundred days ago:

>>> date_offset(r, -400)
datetime.date(2013, 1, 18)


Last day of the month
=====================

Given a date as the only argument to the :func:`last_day_of_month` returns the
last day of the month of the given date. Examples:

>>> last_day_of_month(i2d(20160212))
datetime.date(2016, 2, 29)
>>> last_day_of_month(i2d(20161201))
datetime.date(2016, 12, 31)
>>> last_day_of_month(i2d(20160123))
datetime.date(2016, 1, 31)
>>> last_day_of_month(i2d(20161123))
datetime.date(2016, 11, 30)


Parsing dates
=============

.. currentmodule:: lino.core.site

The historical :meth:`Site.parse_date` method converts a string to a `(y,m,d)`
tuple (not a :class:`datetime.date` instance).

>>> settings.SITE.parse_date("29.02.2024")
(2024, 2, 29)

>>> settings.SITE.parse_date("1234")
Traceback (most recent call last):
...
ValueError: 1234 is not a valid date (format must be dd.mm.yyyy).

Note that the input string *must* be formatted ``dd.mm.yyyy``, which corresponds
to what :attr:`Site.date_format_strftime` or :attr:`Site.date_format_extjs`
return for a :class:`date` object.

>>> settings.SITE.date_format_extjs
'd.m.Y'
>>> settings.SITE.date_format_strftime
'%d.%m.%Y'

If you change these attributes, you must also reimplement
:meth:`Site.parse_date` method.

TODO: these configuration options should get replaced by something more elegant.


Incomplete Date
===============

Examples of :class:`IncompleteDate` instances and their behaviour:

In the case where we have to say something like: "Once upon a time in the year
2011":

>>> print(IncompleteDate(2011, 0, 0).strftime("%d.%m.%Y"))
00.00.2011

Unlike :class:`datetime.date` objects, an incomplete date can hold years
before 1970.

>>> print(IncompleteDate(1532, 0, 0))
1532-00-00

On June 1st (but we don't say the year):

>>> print(IncompleteDate(0, 6, 1))
0000-06-01

On the first day of the month in 1990:

>>> print(IncompleteDate(1990, 0, 1))
1990-00-01

W.A. Mozart's birth date:

>>> print(IncompleteDate(1756, 1, 27))
1756-01-27

Christ's birth date:

>>> print(IncompleteDate(-7, 12, 25))
-7-12-25
>>> print(IncompleteDate(-7, 12, 25).strftime("%d.%m.%Y"))
25.12.-7

Note that you cannot convert all incomplete dates
to real datetime.date objects:

>>> IncompleteDate(-7, 12, 25).as_date()
... #doctest: +ELLIPSIS
Traceback (most recent call last):
...
ValueError: year...is out of range

>>> IncompleteDate(1756, 1, 27).as_date()
datetime.date(1756, 1, 27)

An IncompleteDate is allowed to be complete:

>>> d = IncompleteDate.parse('2011-11-19')
>>> print(d)
2011-11-19
>>> d.is_complete()
True
>>> print(repr(d.as_date()))
datetime.date(2011, 11, 19)

>>> d = IncompleteDate.parse('2008-03-24')
>>> d.get_age(i2d(20131224))
5
>>> d.get_age(i2d(20140323))
5
>>> d.get_age(i2d(20140324))
6
>>> d.get_age(i2d(20140325))
6
>>> d.get_age(i2d(20141025))
6

Note that IncompleteDate can store invalid dates:

>>> d = IncompleteDate(2009, 2, 30)
>>> d.get_age(i2d(20160202))
6

>>> IncompleteDate(2009, 2, 32)
IncompleteDate('2009-02-32')

>>> IncompleteDate(2009, 32, 123)
IncompleteDate('2009-32-123')


Some usage example of the method :meth:`IncompleteDate.parse` which return an
:class:`IncompleteDate` instance:

>>> IncompleteDate.parse('2008-03-24')
IncompleteDate('2008-03-24')

Belgian eID cards gave us some special challenges:

>>> IncompleteDate.parse('01.JUN. 1968')
IncompleteDate('1968-06-01')

>>> IncompleteDate.parse('JUN. 1968')
IncompleteDate('1968-06-00')

>>> IncompleteDate.parse('13 maart 1953')
IncompleteDate('1953-03-13')

>>> IncompleteDate.parse('13 januari 1953')
IncompleteDate('1953-01-13')

Return None when we could not understand the string.

>>> IncompleteDate.parse('foo bar')

dateparser unfortunately does not understand that "MAAR" is the
abbreviation for dutch "MAART" (which means "March"). So here it returns
None:

>>> IncompleteDate.parse('13 MAAR 1953')

Calculating workdays
====================

The function :func:`workdays` calculates and returns the number of working days,
given a start date and an end date.

Examples:

>>> examples = [
...   (20121130,20121201,1),
...   (20121130,20121224,17),
...   (20121130,20121130,1),
...   (20121201,20121201,0),
...   (20121201,20121202,0),
...   (20121201,20121203,1),
...   (20121130,20121207,6),
... ]
>>> for start,end,expected in examples:
...     a = i2d(start)
...     b = i2d(end)
...     if workdays(a,b) != expected:
...        print("Got %d instead of %d for (%s,%s)" % (workdays(a,b),expected,a,b))

Like :func:`workdays`, :func:`dates.weekdays` also works in a similar
fashion. Examples:

>>> from lino.utils.dates import weekdays
>>> weekdays(i2d(20151201), i2d(20151231))
23
>>> weekdays(i2d(20160701), i2d(20160717))
11
>>> weekdays(i2d(20160717), i2d(20160717))
0
>>> weekdays(i2d(20160718), i2d(20160717))
0

Date formatting
===============

There are different date formatting syntaxes:

- `Babel <http://babel.pocoo.org/en/latest/dates.html#date-fields>`__
- `Django <https://docs.djangoproject.com/en/5.0/ref/templates/builtins/#date>`__

The format depends on the current language (given by Django),

.. currentmodule:: lino.utils.format_date

Lino's :func:`format_date` function is a thin wrapper to the corresponding
function in :mod:`babel.dates`, filling the `locale` parameter according to
Django's current language. The major advantage over using :func:`date_format`
rather than :mod:`django.utils.formats` is that Babel offers a "full" format.

The Django language code needs a bit of conversion before passing it to Babel,
because Babel uses a slightly stricter syntax than Django.  The `Django docs
<https://docs.djangoproject.com/en/5.1/topics/i18n/>`__ speaks about these
different syntaxes. We do this conversion in :func:`to_locale
<lino.core.site.to_locale>`.

>>> from lino.core.site import to_locale

>>> to_locale('en-UK')
'en_UK'

>>> to_locale('de-be')
'de_BE'

When no language variant is specified in your :attr:`languages
<lino.core.site.Site.languages>` setting, we leave the decision to Babel. Except
for English. For English we change the default variant from US to UK because US
date format is just silly when you aren't used to it. First the month, then the
day and finally the year! If you insist on having US date format, you must
specify ``en-US`` instead of just ``en``.

Examples of formatting date using the functions :func:`format_date.fds`,
:func:`format_date.fdm`, :func:`format_date.fdl` & :func:`format_date.fdf` which
ultimately calls the function :func:`format_date.format_date` with the related
arguments:


>>> from lino.utils.format_date import *
>>> import datetime
>>> d = datetime.date(2013, 8, 26)
>>> print(fds(d)) # short
26/08/2013
>>> print(fdm(d)) # medium
26 Aug 2013
>>> print(fdl(d)) # long
26 August 2013
>>> print(fdf(d)) # full
Monday, 26 August 2013
>>> print(fdmy(d)) # full
August 2013

Some localized examples of date formatting:

>>> today = datetime.date(2013,1,18)

>>> print(format_date(today,'full'))
Friday, 18 January 2013

>>> with translation.override('fr'):
...    print(format_date(today,'full'))
vendredi 18 janvier 2013

>>> with translation.override('de'):
...    print(format_date(today,'full'))
Freitag, 18. Januar 2013

>>> with translation.override('en_US'):
...    print(format_date(today,'full'))
Friday, January 18, 2013


You can use this also for languages that aren't on your site:

>>> with translation.override('et'):
...    print(format_date(today,'full'))
reede, 18. jaanuar 2013

>>> with translation.override('nl'):
...    print(format_date(today,'full'))
vrijdag 18 januari 2013


>>> with translation.override('de'):
...    print(fds(today))
18.01.13
>>> with translation.override('fr'):
...    print(fds(today))
18/01/2013
>>> with translation.override('en_US'):
...    print(fds(today))
1/18/13
>>> with translation.override('en'):
...    print(fds(today))
18/01/2013
>>> with translation.override('en_UK'):
...    print(fds(today))
18/01/2013


>>> print(fds('')) # empty string is tolerated
<BLANKLINE>
>>> print(fds('2014-10-12')) # not tolerated
Traceback (most recent call last):
  ...
Exception: Not a date: '2014-10-12'


Formatting time values
========================

.. currentmodule:: lino.utils.format_date

>>> print(fts(datetime.time(9,23,15)))
09:23



.. _dg.formatting.timestamps:

Formatting timestamps
========================

.. currentmodule:: lino.utils.format_date


The functions :func:`fdtl` and :func:`fdtf` stand for "format timestamp long" and
"format timestamp full".

The :func:`fdtl` function uses the site settings :attr:`date_format_strftime
<lino.core.site.Site.date_format_strftime>` and :attr:`time_format_strftime
<lino.core.site.Site.time_format_strftime>`.

The :func:`fdtf` function returns :func:`fdtl` and adds Django's
:func:`naturaltime`.

>>> print(fdtl(datetime.datetime(2025,3,31,14,54,0)))  #doctest: +ELLIPSIS
31.03.2025 14:54

>>> from django.utils import timezone
>>> from datetime import timedelta
>>> now = timezone.now

>>> print("\n"+fdtf(now()+timedelta(minutes=10)))  #doctest: +ELLIPSIS
<BLANKLINE>
... ... (9 minutes from now)
