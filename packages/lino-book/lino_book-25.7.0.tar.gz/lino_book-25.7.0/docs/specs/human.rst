.. doctest docs/specs/human.rst
.. _lino.specs.human:
.. _lino.tutorial.human:

===================
The ``Human`` mixin
===================

.. currentmodule:: lino.mixins.human

This article explains the :class:`lino.mixins.human.Human` model mixin.

.. contents::
   :depth: 1
   :local:


.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.avanti1.startup import *
>>> from django.db.models import Q
>>> from django.utils import translation
>>> Person = contacts.Person
>>> Genders = system.Genders


Database structure
==================

This tutorial uses the demo database in :mod:`lino_book.projects.avanti1`, which
uses the :class:`lino_xl.lib.contacts.Person` model, which inherits from
:class:`lino.mixins.human.Human`. (It also inherits from
:class:`lino.mixins.human.Born`, explained in  :doc:`born`.)


Basic human values
==================

The :class:`Human` model mixin defines four database fields `first_name`,
`middle_name`, `last_name` and `gender`.

The `gender` field is a pointer to the :class:`lino.modlib.system.Genders`
choicelist and its value is used for :ref:`salutation <human.salutation>`
or by :ref:`the mf() method <human.mf>`.

All these fields may be blank (except if your application changed that
rule using :func:`lino.core.inject.update_field`).

Parsing names
=============

>>> from lino.mixins.human import name2kw

Examples:

>>> name2kw("Saffre Luc") == {'first_name': 'Luc', 'last_name': 'Saffre'}
True
>>> name2kw("Rilke Rainer Maria") == {'first_name': 'Rainer Maria', 'last_name': 'Rilke'}
True
>>> name2kw("Van Rompuy Herman") == {'first_name': 'Herman', 'last_name': 'Van Rompuy'}
True
>>> name2kw("'T Jampens Jan") == {'first_name': 'Jan', 'last_name': "'T Jampens"}
True
>>> name2kw("Van den Bossche Marc Antoine Bernard") == {'first_name': 'Marc Antoine Bernard', 'last_name': 'Van den Bossche'}
True
>>> name2kw("Den Tandt Marc Antoine Bernard") == {'first_name': 'Marc Antoine Bernard', 'last_name': 'Den Tandt'}
True


In more complicated cases, a comma is required to help:

>>> name2kw("Mombanga born Ngungi, Maria Magdalena") == {'first_name': 'Maria Magdalena', 'last_name': 'Mombanga born Ngungi'}
True

Some examples with `first_name` first:

>>> name2kw("Luc Saffre", False) == {'first_name': 'Luc', 'last_name': 'Saffre'}
True

>>> name2kw("Rainer Maria Rilke", False) == {'first_name': 'Rainer Maria', 'last_name': 'Rilke'}
True

>>> name2kw("Herman Van Rompuy", False) == {'first_name': 'Herman', 'last_name': 'Van Rompuy'}
True

>>> name2kw("Jan 'T Jampens", False) == {'first_name': 'Jan', 'last_name': "'T Jampens"}
True
>>> name2kw("Marc Antoine Bernard Van den Bossche", False) == {'first_name': 'Marc Antoine Bernard', 'last_name': 'Van den Bossche'}
True
>>> name2kw("Marc Antoine Bernard Den Tandt", False) == {'first_name': 'Marc Antoine Bernard', 'last_name': 'Den Tandt'}
True

Some examples taken from
`a question on SO
<https://stackoverflow.com/questions/48383199/splitting-names-that-include-de-da-etc-into-first-middle-last-etc>`__
with Brazilian names:

>>> name2kw("Emiliano Rodrigo Carrasco", False) == {'first_name': 'Emiliano Rodrigo', 'last_name': 'Carrasco'}
True
>>> name2kw("Alberto de Francia", False) == {'first_name': 'Alberto', 'last_name': 'de Francia'}
True

TODO: This one doesn't yet work:

>>> # name2kw("Francisco da Sousa Rodrigues", False)

Edge cases:

>>> name2kw("")
{}

Bibliography:

#. https://en.wikipedia.org/wiki/Dutch_name
#. https://en.wikipedia.org/wiki/Tussenvoegsel
#. https://www.myheritage.com/support-post-130501/dutch-belgium-german-french-surnames-with-prefix-such-as-van



Examples:

>>> from lino.mixins.human import parse_name

>>> pprint(parse_name("luc saffre"))
{'first_name': 'Luc', 'last_name': 'Saffre'}

But careful with name prefixes:

>>> pprint(parse_name("herman van veen"))
{'first_name': 'Herman', 'last_name': 'van veen'}

>>> pprint(parse_name("jean van den bossche"))
{'first_name': 'Jean', 'last_name': 'van den bossche'}

>>> parse_name("Foo")  #doctest: +ELLIPSIS +IGNORE_EXCEPTION_DETAIL
Traceback (most recent call last):
...
ValidationError: ...Cannot find first and last name in "Foo"']


.. _human.salutation:

Salutation
==========

The default :meth:`__str__` method of a Human includes the "salutation", which
indicates the gender:

>>> print(Person(first_name="John", last_name="Smith", gender=Genders.male))
Mr John Smith

>>> print(Person(last_name="Smith", gender=Genders.female))
Mrs Smith

If you don't specify a gender, Lino doesn't print any salutation:

>>> print(Person(first_name="John", last_name="Smith"))
John Smith

>>> print(Person(first_name="John"))
John

The salutation depends not only on the gender, but also on the
current language.
This is Mr Jean Dupont:

>>> p = Person(first_name="Jean", last_name="Dupont", gender=Genders.male)

We can address him in English:

>>> print(p)
Mr Jean Dupont

The same object will render differently when we switch to French...

>>> with translation.override('fr'):
...     print(p)
M. Jean Dupont

... or to German...

>>> with translation.override('de'):
...     print(p)
Herr Jean Dupont



The full name
=============

Calling `str` on a person actually returns the same as the property `full_name`:

>>> print(p)
Mr Jean Dupont

>>> print(p.full_name)
Mr Jean Dupont

They are equivalent *here*, but remember that applications may override one of
them (usually `__str__`) because in reality not all humans are equal.

>>> print(p.get_full_name())
Mr Jean Dupont

The :func:`get_full_name <lino.mixins.human.Human.get_full_name>`
function has 2 optional parameters `nominative` and `salutation`.

In some languages, for example German, the salutation may vary depending on
whether you talk about them or whether you address them directly. In the latter
case you need to use the nominative form.

>>> with translation.override('de'):
...     print(p.get_full_name())
...     print(p.get_full_name(nominative=True))
Herrn Jean Dupont
Herr Jean Dupont

You may want to omit the salutation:

>>> with translation.override('de'):
...     print(p.get_full_name(salutation=False))
Jean Dupont

The property `full_name` (without parentheses) of Person
is an alias for the function call `get_full_name()` without parameters.

>>> with translation.override('de'):
...    print(p.full_name)
Herrn Jean Dupont





Uppercase last name
===================

In France it is usual to print the last name with captial letters.

>>> with translation.override('fr'):
...    print(p.get_full_name(upper=True))
M. Jean DUPONT

Lino also has a setting :setting:`uppercase_last_name` which causes
this to be the default.

>>> from django.conf import settings
>>> settings.SITE.uppercase_last_name = True

>>> with translation.override('fr'):
...     print(p)
M. Jean DUPONT

When :setting:`uppercase_last_name` is set to True and you
(exceptionally) do *not* want uppercase last names, then you must
specify it explicitly:

>>> with translation.override('fr'):
...    print(p.get_full_name(upper=False))
M. Jean Dupont


The title of a human
====================

The :attr:`title` field of a human is for specifying a `title
<https://en.wikipedia.org/wiki/Title>`__ such as "Dr." or "PhD".

>>> settings.SITE.uppercase_last_name = False
>>> p.title = "Dr."
>>> p.full_clean()
>>> print(p.get_full_name())
Mr Dr. Jean Dupont
>>> with translation.override('de'):
...     print(p.get_full_name())
Herrn Dr. Jean Dupont


In :mod:`lino_xl.lib.contacts` this is covered by the
:attr:`lino_xl.lib.contacts.Partner.prefix` field.

.. _human.mf:

The `mf` method
===============

The :meth:`mf <lino.mixins.human.Human.mf>` method of a Human
is useful in document templates when you want to generate texts
that differ depending on the gender of a Human.

>>> mankind = [Person(first_name="Adam", gender=Genders.male),
...   Person(first_name="Eva", gender=Genders.female)]

>>> def about(p):
...     return "{} was the first {}.".format(
...         p, p.mf("man", "woman"))
>>> for p in mankind:
...     print(about(p))
Mr Adam was the first man.
Mrs Eva was the first woman.


The `mf` method is a bit sexistic in that it returns the male value
when the `gender` field is blank:

>>> p = Person(first_name="Conchita", last_name="Wurst")
>>> print(p.mf("He", "She"))
He

Templates can use the third argument to handle this case properly:

>>> print(p.mf("He", "She", "He or she"))
He or she



The `strip_name_prefix` function
================================

>>> from lino.mixins.human import strip_name_prefix
>>> strip_name_prefix("Vandenberg")
'VANDENBERG'

>>> strip_name_prefix("Van den Berg")
'BERG'

>>> strip_name_prefix("Vonnegut")
'VONNEGUT'

>>> strip_name_prefix("von Goethe")
'GOETHE'

>>> strip_name_prefix("Jean")
'JEAN'

>>> strip_name_prefix("Jean-Jacques")
'JEAN-JACQUES'

>>> strip_name_prefix("Nemard")
'NEMARD'
