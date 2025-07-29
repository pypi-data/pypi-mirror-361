.. doctest docs/dev/diamond.rst
.. _lino.tested.diamond:
.. _lino.tested.diamond2:

===================
Diamond inheritance
===================

The :mod:`lino_book.projects.diamond` project was used  in ancient times (before
Django 1.11) to test a workaround for some problems with **diamond inheritance**.

Here is an example of diamond inheritance:


.. graphviz::

   digraph foo {
      Addressable -> Restaurant
      Restaurant -> Bar
      Restaurant -> Pizzeria
      Pizzeria -> PizzaBar
      Bar -> PizzaBar
  }


.. literalinclude:: /../lino_book/projects/diamond/main/models.py



The problem
===========

>>> from lino import startup
>>> startup('lino_book.projects.diamond.settings')
>>> from lino.api.doctest import *

>>> p = main.PizzaBar(name="A", min_age="B", specialty="C",
...     pizza_bar_specific_field="Doodle", street="E")

Despite the fact that we specify a non-blank value for `name`, we had a database
object whose `name` is blank, while the `pizza_bar_specific_field` field is not:

>>> print(p.name)
A
>>> print(p.pizza_bar_specific_field)
Doodle
>>> print(p.street)
E


Some Django versions raises a `django.core.exceptions.FieldError` saying that
"Local field u'street' in class 'PizzeriaBar' clashes with field of the same
name from base class 'Pizzeria'".

The `street` field is defined in *a parent of* the common
parent. Django then got messed up when testing for duplicate fields and
incorrectly thinks that `street` is duplicated.


See Django ticket :djangoticket:`10808`.
