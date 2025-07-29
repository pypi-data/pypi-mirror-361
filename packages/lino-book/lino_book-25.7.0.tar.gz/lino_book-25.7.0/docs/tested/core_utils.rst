.. doctest docs/tested/core_utils.rst
.. _tested.core_utils:

Lino core utilities
===================

This document tests some functionality of :mod:`lino.core.utils`.


.. contents::
   :depth: 1
   :local:

.. include:: /../docs/shared/include/tested.rst

>>> import lino
>>> lino.startup('lino_book.projects.min2.settings.demo')
>>> from lino.api.doctest import *



Get installed models that are subclass of something
======================================================

The :func:`lino.core.utils.models_by_base` function returns a list of
models which are subclass of a given class.

For example here is how you can get all your models that implement
:class:`lino.mixins.duplicable.Duplicable`:

>>> from lino.mixins.duplicable import Duplicable
>>> pprint(rt.models_by_base(Duplicable))  #doctest: +NORMALIZE_WHITESPACE +REPORT_UDIFF
[<class 'lino_xl.lib.cal.models.Event'>,
 <class 'lino_xl.lib.cal.models.EventType'>,
 <class 'lino_xl.lib.cal.models.RemoteCalendar'>,
 <class 'lino_xl.lib.contacts.models.Company'>,
 <class 'lino_xl.lib.contacts.models.Partner'>,
 <class 'lino_xl.lib.contacts.models.Person'>,
 <class 'lino_xl.lib.countries.models.Place'>,
 <class 'lino.modlib.linod.models.SystemTask'>]


>>> rt.models_by_base(rt.models.contacts.Person)
[<class 'lino_xl.lib.contacts.models.Person'>]

.. rubric:: Getting only top-level models

The `toplevel_only` option is used by :mod:`lino.modlib.checkdata`.
For example the
:class:`AddressOwnerChecker
<lino.modlib.addresses.mixins.AddressOwnerChecker>` needs to run only on
Partner, not also on Person, Company, Household or any other MTI children.

>>> rt.models_by_base(rt.models.contacts.Partner, toplevel_only=True)
[<class 'lino_xl.lib.contacts.models.Partner'>]

>>> rt.models_by_base(rt.models.contacts.Person, toplevel_only=True)
[<class 'lino_xl.lib.contacts.models.Person'>]
