.. doctest docs/dev/quantities.rst
.. _book.dev.quantities:

==========
Quantities
==========

.. currentmodule:: lino.core.fields

This document explains Lino's database fields :class:`DurationField` and
:class:`QuantityField`.

.. contents::
   :depth: 1
   :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.cosi3.startup import *
>>> from lino.utils.quantities import parse, DEC2HOUR, Duration, Percentage, Quantity
>>> import datetime
>>> from decimal import Decimal


Overview
========


.. currentmodule: lino.utils.quantities

Quantities are defined in the :mod:`lino.utils.quantities` module.

A **quantity** is a type of decimal number used for business documents.
A **duration** is a quantity expressed in ``hh:mm`` format.
A **percentage** is a quantity expressed in ``x%`` format.

All quantity fields are subclasses of :class:`CharField`, and their values are
stored in the database as text.

The :class:`Quantity` class is a subclass of :class:`Decimal`. The only
difference between them is that a Quantity has a :func:`len` in order to satisfy
Django's :class:`CharField` validators.

The value of a :class:`QuantityField` is a :class:`Quantity`, which is a
subclass of :class:`Decimal`.

The :func:`parse` function decides which subclass of quantity to use. It is
used internally by :class:`QuantityField`.

>>> parse('1:15')
Duration('1:15')
>>> parse('33%')
Percentage('33%')
>>> parse('1')
Quantity('1')


TODO: You cannot currently instantiate a :class:`Quantity` from a string that
represents a duration or a percentage.

>>> Quantity('1:15')
Traceback (most recent call last):
...
decimal.InvalidOperation: [<class 'decimal.ConversionSyntax'>]

>>> Quantity('4%')
Traceback (most recent call last):
...
decimal.InvalidOperation: [<class 'decimal.ConversionSyntax'>]

But you can cast durations and percentages to a :class:`Quality` instance:

>>> Quantity(Duration('1:15'))
Quantity('1:15')

>>> Quantity(Percentage('4%'))
Quantity('4%')


Durations
=========

A :class:`Duration` expresses a duration in `hours:minutes`.

>>> print(Duration('1:00'))
1:00
>>> print(Duration('1:30'))
1:30
>>> print(Duration('1:55'))
1:55

>>> print(Duration('1:45') * 2)
3:30
>>> print(Duration('1:55') * 2)
3:50

>>> print(Duration('0:45') / 3)
0:15

>>> print(Duration('0:49') / 10)
0:05

>>> print(Duration('1:30') * 2)
3:00
>>> print(Duration('0:03') * 10)
0:30
>>> print(Duration('0:01') * 60)
1:00
>>> print(Duration('0:01') * 6000)
100:00

>>> print(2 * Duration('1:30'))
3:00
>>> print(30 * Duration('0:20'))
10:00


>>> print(Duration('1:55') + Duration('0:05'))
2:00
>>> print(Duration('1:55') + Duration('0:10'))
2:05

>>> print(Duration('1:55') - Duration('0:10'))
1:45
>>> print(Duration('1:05') - Duration('0:10'))
0:55
>>> print(Duration('8:30') + Duration('1:00'))
9:30

Durations can be more than 24 hours
===================================

A duration can be more than 24 hours, and in that case (unlike
:class:`datetime.datetime`) it is still represented using
`hhhh.mm`:

>>> print(Duration(datetime.timedelta(hours=25)))
25:00

>>> print(Duration(datetime.timedelta(days=128)))
3072:00

>>> print(Duration(datetime.timedelta(0, minutes=24*60+5)))
24:05

>>> print(Duration(datetime.timedelta(1, minutes=5)))
24:05

>>> Duration('125:10') + Duration('524:12')
Duration('649:22')

>>> Duration(630.25)
Duration('630:15')

Durations and datetime
======================

You can add a duration to a datetime:

>>> datetime.datetime(2019, 4, 3, 23, 45) + Duration("0:30")
datetime.datetime(2019, 4, 4, 0, 15)

Or substract it from a datetime:

>>> datetime.datetime(2019, 4, 3, 0, 15) - Duration("0:30")
datetime.datetime(2019, 4, 2, 23, 45)

Also when the duration is longer than a day:

>>> datetime.datetime(2019, 4, 3, 16, 53) + Duration("36:00")
datetime.datetime(2019, 4, 5, 4, 53)

>>> print(Duration(datetime.timedelta(0)))
0:00
>>> print(Duration(datetime.timedelta(0, hours=10)))
10:00
>>> print(Duration(datetime.timedelta(0, minutes=10)))
0:10

Durations and quantities
========================

>>> print(Quantity(1) * Duration('5:00'))
5:00

>>> print(Quantity(2) * Duration('1:20'))
2:40

>>> print(Quantity(2.5) * Duration('1:20'))
3:20


Convert duration to decimal:

>>> print(Decimal(Duration('1:30')))
1.500000000000000000000000000
>>> print(Decimal(Duration('1:20')))
1.333333333333333333333333333


Durations and numbers
======================

When a duration is combined with a normal ("decimal") number, the
duration is interpreted as a number hours.


>>> 12 - Duration("0:05")
Duration('11:55')

>>> 12 + Duration("0:05")
Duration('12:05')

>>> Duration("0:05") + 12
Duration('12:05')

>>> Decimal(Duration("0:05"))
Decimal('0.08333333333333333333333333335')

>>> Decimal(Duration("1:30"))
Decimal('1.500000000000000000000000000')


Lino converts decimal values to durations as expected:

>>> print(Duration('1'))
1:00
>>> print(Duration('2.5'))
2:30
>>> print(Duration('2.50'))
2:30
>>> print(Duration('0.33'))
0:20
>>> print(Duration('0.30'))
0:18



Difference between DurationField and TimeField
==============================================

A :class:`lino.core.fields.DurationField` might look similar to a
:class:`lino.core.fields.TimeField` or a standard Django :class:`TimeField`.
But keep in mind:

A DurationField is to store a **number of hours (and minutes)** while a time
field contains the time part of a timestamp.  A duration can be more than 24
hours, it can be negative.

You cannot instantiate from :class:`datetime.time` object:

>>> print(Duration(datetime.time(hour=1, minute=28)))
Traceback (most recent call last):
...
ValueError: Cannot convert datetime.time(1, 28) to Duration



Computing with durations
========================

Mathematical operations on durations

add and subtract

>>> Duration('1:45') + Duration('1:15')
Duration('3:00')
>>> Duration('1:45') - Duration('1:15')
Duration('0:30')

>>> d = Duration('1:45')
>>> d += Duration('2:15')
>>> d
Duration('4:00')
>>> d -= Duration('0:15')
>>> d
Duration('3:45')

multiply

>>> print(Duration('2:30') * 3)
7:30

>>> print(Duration('2:30') * 100)
250:00

>>> print(Duration('0:20') * 3)
1:00

>>> print(Duration('0:20') * 100)
33:20


Formatting
==========

>>> print(Duration("0.33334"))
0:20
>>> print(Duration("0.50"))
0:30


Decimal separator
=================

Both period and comma are accepted as decimal separator:

>>> parse('1.5')
Quantity('1.5')
>>> parse('1,5')
Quantity('1.5')

But you may not use both at the same time:

>>> parse('1,000.50')
Traceback (most recent call last):
...
ValueError: Invalid decimal value '1,000.50'


Durations and invoices
========================

The *quantity* field of invoices (:attr:`lino_xl.lib.vat.QtyProductItem.qty`)
is a :class:`QuantityField <lino.core.fields.QuantityField>`).  This is
handy when invoicing services per hour.  For example when you have a hourly
rate of 60€ and worked 20 minutes, you can write '0:20' as quantity and don't
need to convert this to a decimal value ('0.33'):

>>> hourly_rate = Decimal('60.00')

>>> print(hourly_rate * Duration('0:20'))
20:00

>>> print(hourly_rate * Decimal('0.33'))
19.8000

And as you can see, you save 20 cents.  You might work around the rounding
problem by adding decimal places to the quantity field, but this is ugly and
remains a workaround:

>>> print(hourly_rate * Decimal('0.333'))
19.98000

>>> print(hourly_rate * Decimal('0.3333'))
19.998000


Percentages
===========

>>> Percentage('10%')
Percentage('10%')

TODO: The following uses cases are not yet very stable.

>>> Percentage('10')
Percentage('10%')

>>> print(Percentage("0.50"))
0.50%
>>> print(Percentage("0.33334"))
0.33334%


Multiplying a decimal with a percentage yields a decimal:

>>> 100 * Percentage('33%')
Decimal('33.00')

>>> Decimal("100.00") * Percentage("33%")
Decimal('33.0000')

Multiplying a percentage with a decimal yields a percentage:

>>> Percentage('5%') * 3
Percentage('15.00%')

When adding decimals to a percentage, the decimal must have the real value, not
the number of percents:

>>> Percentage('5%') + Decimal('0.03')
Percentage('8.00%')

>>> Decimal('0.03') + Percentage('5%')
Percentage('8.00%')




Discounts
=========

For the following examples we need an invoice item. We don't want to
modify our demo data, so we are not going to save it.

>>> Invoice = rt.models.trading.VatProductInvoice
>>> Item = rt.models.trading.InvoiceItem
>>> Product = rt.models.products.Product
>>> from lino.utils.quantities import Quantity, Percentage, Decimal
>>> # show_fields(Item, all=True)

Pick an existing voucher and product:

>>> voucher = Invoice.objects.all().first()
>>> product = Product.objects.get(pk=1)
>>> product.sales_price
Decimal('199.99')

The :attr:`qty` field is nullable (can be `None`), which means "no value". When
you set a product on an invoice item but no quantity, the amount is computed as
if the quantity was 1.

>>> i = Item(voucher=voucher, product=product)
>>> i.product_changed()
>>> i.unit_price
Decimal('199.99')
>>> i.total_incl
Decimal('199.99')
>>> i.total_base
Decimal('166.66')
>>> print(i.qty)
None

>>> dd.plugins.vat.item_vat
True

>>> i.full_clean()
>>> ar = rt.login("robin")
>>> print(i.as_paragraph(ar))
<a href="…">2) Wooden table</a> &mdash; for € 199,99 (€ 166,66 + VAT € 33,33)


You can manually change the quantity to 2, which will update the total price:

>>> i.qty = parse("2")
>>> i.qty_changed()
>>> i.total_incl
Decimal('399.98')

>>> print(i.as_paragraph(ar))
<a href="…">2) Wooden table</a> &mdash; 2 Pieces à € 199,99 = € 399,98 (€ 333,32 + VAT € 66,66)

You can give a discount of 10 %:

>>> i.discount_rate = Decimal("10")
>>> i.discount_rate_changed()
>>> i.total_incl
Decimal('359.98')

>>> print(i.as_paragraph(ar))
<a href="…">2) Wooden table</a> &mdash; 2 Pieces à € 199,99 - 10% = € 359,98 (€ 299,98 + VAT € 60,00)


Note that :class:`PercentageField <lino.core.fields.PercentageField>` doesn't
use :mod:`lino.utils.quantities` for historical reasons.  This field is
currently just a thin wrapper around :class:`DecimalField`, and Lino adds a
percent sign when printing it.  One day we might change this (:ticket:`2941`).

You can manually set the quantity to 0:

>>> i.qty = parse("0")
>>> i.qty_changed()
>>> i.total_incl
Decimal('0.00')

You can have invoice lines without any product:

>>> i = Item(voucher=voucher)
>>> print(repr(i.qty))
None
>>> i.reset_totals()
>>> i.set_amount(None, Decimal("100"))
>>> i.total_incl
Decimal('100.00')

>>> print(repr(i.qty))
None

>>> def test_qty(**kwargs):
...     i = Item(voucher=voucher, **kwargs)
...     i.full_clean()
...     print(repr(i.qty))

>>> test_qty(qty=None)
None
>>> test_qty(qty=30)
Quantity('30')
>>> test_qty(qty='')
''
>>> test_qty(qty=0)
None

Note that :class:`QuantityField <lino.core.fields.QuantityField>` returns the
particular subclass of :class:`Quantity`:

>>> test_qty(qty="4.5%")
Percentage('4.5%')
>>> test_qty(qty="2:30")
Duration('2:30')

>>> test_qty(qty=Duration('2:30'))
Duration('2:30')

If you try to store a quantity that requires more than the `max_length` of the
field, Lino will try to limit its length by calling
:meth:`Quantity.limit_length`:

>>> trading.InvoiceItem._meta.get_field('qty').max_length
6
>>> test_qty(qty='1234.56')  #doctest: +ELLIPSIS
Quantity('1234.6')

>>> Quantity('1234.56').limit_length(6)
Quantity('1234.6')
>>> Quantity('1234.56').limit_length(5)
Quantity('1235')
>>> Quantity('1234.56').limit_length(4)
Quantity('1235')

You cannot work in all cases, though:

>>> Quantity('1234.56').limit_length(3)
Traceback (most recent call last):
...
Exception: Cannot reduce length of 1234.56 to 3

For durations there is no way to limit the length:

>>> Duration('1234:30').limit_length(6)
Traceback (most recent call last):
...
Exception: Cannot reduce length of 1234:30 to 6



Utilities
=========

>>> DEC2HOUR
Decimal('0.01666666666666666666666666667')


Migrations and serializing
==========================

>>> Duration("2:30") == Duration("2:30")
True

>>> Duration("2:30") != Duration("2:30")
False

Quantities have a `custom deconstruct method
<https://docs.djangoproject.com/en/5.0/topics/migrations/#adding-a-deconstruct-method>`__:

>>> Duration("2:30").deconstruct()
('lino.utils.quantities.Duration', ('2:30',), {})

.. _dg.quantities.pitfall:

A possible pitfall
==================

Here is a possible pitfall. The following example shows two durations that *look*
the same but actually aren't:

>>> d1 = Duration("1:40") / 3
>>> d1
Duration('0:33')
>>> d2 = Duration("0:33")
>>> d2
Duration('0:33')

>>> d1 == d2
False

A plain Decimal does not have this pitfall:

>>> d1 = Decimal("100") / 3
>>> d1
Decimal('33.33333333333333333333333333')

>>> d2 = Decimal('33.33333333333333333333333333')

>>> d2
Decimal('33.33333333333333333333333333')

>>> d1 == d2
True

.. _negative_durations:

Negative durations
==================

>>> - Duration('1:45')
Duration('-1:45')

>>> Duration('-1:45')
Duration('-1:45')

>>> Duration(-1.75)
Duration('-1:45')

>>> Decimal(Duration('-1:45'))
Decimal('-1.750000000000000000000000000')

>>> Duration('-1:45') + Duration('-1:15')
Duration('-3:00')

>>> Duration('-5:00') < Duration('1:00')
True


.. _dg.quantities.format:

Using durations with ``string.format()``
========================================

Since 20230127, Quantity overrides the :meth:`str.__format__`  method,
which is used when inserting a duration into a string with :meth:`format`.

>>> d = Duration("1:30")
>>> "Duration is {}".format(d)
'Duration is 1:30'

>>> "Percentage is {}".format(Percentage("5%"))
'Percentage is 5%'

If the template string specifies a format spec you
probably want to call :func:`str` on the value because otherwise the duration
will be formatted like a Decimal.

>>> "{:>7}".format(d)
'   1:30'

This pitfall does not apply to the old ``%`` operator:

>>> "%s" % d
'1:30'


>>> d = Duration(-12345.50)
>>> "{:>10}".format(d)
' -12345:30'

>>> "{:>5}".format(d)
'-12345:30'


.. _dg.quantities.eq:

Rich comparison
=======================


>>> Duration("2:30") == Quantity(2.5)
True

>>> Quantity("2.50") == Quantity(2.5)
True

>>> Duration('-42:40') == Quantity(Duration('-42:40'))
True

TODO: The following cases show that quantities can cause surprising behaviour
caused rounding issues:

>>> Duration(1/3)
Duration('0:20')

>>> Duration(1/3) == Duration('0:20')
False

>>> value = Duration('-42:40') + Decimal('0.00001')
>>> value
Duration('-42:40')

>>> Duration('-42:40') == value
False



Class reference
===============

.. currentmodule:: lino.utils.quantities

.. class:: Quantity

  The base class for all *quantities*.

  .. method:: limit_length(max_length, excl=Exception)

    Reduce the number of decimal places so that the value fits into a field of
    the specified `max_length`, if possible. This will round the value (reducing
    precision) if needed.

    Raise an exception "Cannot reduce length of {value} to {max_length}" if the
    value can't be rendered even when there are no decimal places at all.


.. class:: Duration

    The class to represent a **duration**.

.. class:: Percentage

    The class to represent a **percentage**.

.. class:: Fraction

    The class to represent a **fraction**. (Not yet implemented)
