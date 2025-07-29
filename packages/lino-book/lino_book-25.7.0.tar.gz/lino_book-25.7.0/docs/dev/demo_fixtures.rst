.. _demo_fixtures:

=============================
Introduction to demo fixtures
=============================

Django fixtures
===============

A **fixture**, in real life, is a piece of furniture in a house, such as a
kitchen, that is considered an integral part of the house. Django uses the word
to designate a collection of data records that can be loaded into the database
of a new site. The Django docs have a whole Topic guide about `How to provide
initial data for models
<https://docs.djangoproject.com/en/5.0/howto/initial-data/>`__.

Every :term:`plugin` can have a subdirectory named :xfile:`fixtures`. Django
will discover this directory when you run the :manage:`loaddata` command.

.. xfile:: fixtures

  A subdirectory of a :term:`plugin` that contains a number of fixture files in
  different formats to be loaded using the :manage:`loaddata` command.

In Lino we usually don't write fixtures in XML or JSON but :doc:`in Python
</dev/pyfixtures/index>`. That's why our :xfile:`fixtures` directories also
contain a :xfile:`__init__.py` file.

As a future :term:`application developer` you can learn more about them in
:ref:`lino.tutorial.writing_fixtures`.


Demo fixtures
=============

Lino extends Django's :xfile:`fixtures` by defining the concept of :term:`demo
fixtures`.


.. glossary::

  demo fixtures

    The list of fixtures to be loaded by :cmd:`pm prep` when a new Lino site gets
    installed.

For example, the :doc:`chatter </projects/chatter>` application has the
following value for this attribute:

>>> from lino_book.projects.chatter.settings import Site
>>> Site.demo_fixtures
('std', 'demo', 'demo2', 'checkdata')

This means that saying :cmd:`pm prep` on a site that runs :doc:`chatter
</projects/chatter>`  is equivalent to saying :cmd:`pm initdb std demo demo2 <pm
initdb>`.

If the new site runs a :ref:`cosi`, the list of :term:`demo fixtures` is
different:

>>> from lino_cosi.lib.cosi.settings import Site
>>> Site.demo_fixtures
['std', 'minimal_ledger', 'furniture', 'demo', 'demo2', 'demo3', 'checkdata']

The list of :term:`demo fixtures` of an application is defined  by the
:term:`application developer` in the :attr:`demo_fixtures
<lino.core.site.Site.demo_fixtures>` site attribute.

Demo fixtures are written by the :term:`application developer` because the
:term:`system administrator` doesn't need to know them when setting up a Lino
site. The default list of demo fixtures to load for initializing a meaningful
demo database can be long and difficult to remember, it can change when an
application evolves... These are implementation details, which a :term:`system
administrator` doesn't *want* to know.

Further reading
===============

- :doc:`/ref/demo_fixtures`
- :doc:`/dev/pyfixtures/index`
