.. doctest docs/utils/addressable.rst

=====================================
The ``lino.utils.addressable`` module
=====================================

.. currentmodule:: lino.utils.addressable

The :mod:`lino.utils.addressable` module  defines the :class:`Addressable` mixin
and related functionality. It is is used by :mod:`lino_xl.lib.contacts` and
:class:`lino_xl.lib.appypod.PrintLabelsAction`.

The mixin differentiates between the "person" and the "location" part of an
address.  For example::

    Mr. Luc Saffre     | person
    Rumma & Ko OÜ      | person
    Uus 1              | location
    Vana-Vigala küla   | location
    Vigala vald        | location
    Estonia            | location


Address as HTML
===============

The following examples use the class :class:`TestAddress`, which inherits from
the :class:`Addressable` class and does not override any basic functionalities.

>>> from lino.utils.addressable import TestAddress
>>> addr2 = TestAddress('line1', 'line2')
>>> addr3 = TestAddress('line1', 'line2', 'line3')
>>> addr0 = TestAddress()


The method :meth:`Addressable.get_address_html` returns an address formatted as
html. The html markup always contains exactly one paragraph (`<p>`) tag.

If ``min_height`` is specified as a keyword argument, makes sure that the string
contains at least that many lines by adding as many empty lines (``<br/>``) as
needed. This is useful in a template that wants to get a given height for every
address.

>>> print(addr2.get_address_html(min_height=5))
<p>line1<br/>line2<br/><br/><br/></p>

If the address contains more lines than `min_height`, they are printed
nevertheless (and the paragraph contains more than min_hieght lines):

>>> print(addr3.get_address_html(min_height=2))
<p>line1<br/>line2<br/>line3</p>

Any other keyword arguments become attributes for the enclosing paragraph tag:

>>> print(addr2.get_address_html(align="right"))
<p align="right">line1<br/>line2</p>

If you want to specify a `class` attribute, you need to use special syntax
because `class` is a reserved word in Python:

>>> print(addr2.get_address_html(**{'class':"Recipient"}))
<p class="Recipient">line1<br/>line2</p>

The :meth:`get_address_html` internally uses :meth:`etgen.html.lines2p`, which
packs the address lines into a paragraph (see there for more examples).

When the address is empty, the paragraph is empty:

>>> print(addr0.get_address_html())
<p/>

The :meth:`Addressable.has_address` method tells us whether the
:class:`Addressable` instance is a non-empty address object:

>>> addr2.has_address()
True
>>> addr0.has_address()
False
