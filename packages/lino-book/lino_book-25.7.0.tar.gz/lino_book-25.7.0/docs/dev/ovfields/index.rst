.. doctest docs/dev/ovfields/index.rst
.. _dev.ovfields:

=========================
Overriding virtual fields
=========================

Before Django 4, it was not allowed to override a virtual field by a database
field. The opposite direction was allowed already before Django 4, but in the
use case presented below,  Lino raised a ChangedAPI exception to avoid this
pitfall.

For example, you use a library with a model mixin :class:`MyMixin`, which
defines a :term:`virtual field` named :attr:`foo`. You write a model
:class:`MyModel`, based on :class:`MyMixin`. And in your model you define
yourself a field named :attr:`foo`. Maybe you simply didn't know that
:class:`MyMixin` has already a field of that name. But your foo is a
:term:`database field`.

The :mod:`lino_book.projects.ovfields` demo application shows this by defining
the following database model:

.. literalinclude:: /../../book/lino_book/projects/ovfields/models.py


>>> from lino import startup
>>> startup('lino_book.projects.ovfields.settings')
>>> from lino.api.doctest import *

>>> # clean up previous test runs
>>> from django.core.management import call_command
>>> call_command('initdb', interactive=False, verbosity=0)

>>> obj = ovfields.MyModel(foo='bar')
>>> obj.full_clean()
>>> obj.save()
>>> print(obj)
MyModel object (1)

>>> print(obj.foo)
bar

>>> rt.show(ovfields.MyModels)
==== =====
 ID   Foo
---- -----
 1    bar
==== =====
<BLANKLINE>


>>> obj.foo = "new value"
>>> print(obj.foo)
new value

>>> obj.full_clean()
>>> obj.save()

>>> rt.show(ovfields.MyModels)
==== ===========
 ID   Foo
---- -----------
 1    new value
==== ===========
<BLANKLINE>

>>> ovfields.MyModels.get_data_elem('foo')
<lino.core.fields.CharField: foo>

>>> for ql in settings.SITE.get_quicklink_items(None):
...     print(ql)
my models


Above examples show that everything is okay, the code works as expected. Since
Django 4. The issue probably was because Django before version 4 did some magic
during startup, which it no longer does since version 4. When you tried to get
the value of the database field, Python would call the virtual field method and
give you this value.


.. django-4.0 does not generates this exception.

  Traceback (most recent call last):
    ...
  lino.core.exceptions.ChangedAPI: CharField field ovfields.MyModel.foo hidden by virtual field of same name.
