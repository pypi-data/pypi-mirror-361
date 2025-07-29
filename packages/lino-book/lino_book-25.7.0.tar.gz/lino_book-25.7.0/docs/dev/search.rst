.. doctest docs/dev/search.rst

=================================
Customize how data is searched
=================================

As the :term:`application developer` you can customize how :term:`end users <end
user>` can search for data.

Excluding a database model from site-wide searches
==================================================

If you want a given model to never occur in the :term:`site-wide search window`,
then you can set its :attr:`Model.show_in_site_search` to `False`.

.. currentmodule:: lino.core.model

.. class:: Model
  :noindex:

  .. attribute:: show_in_site_search = True

    Whether this model is to be included in the :term:`site-wide search window`.


Customizing where quick search should search
============================================

The following two model attributes customize which fields to search when the
:term:`quick search field` is used.

.. class:: Model
  :noindex:

  .. attribute:: quick_search_fields = None

    The fields to be included in queries with a quick search value.

    If you don't specify it, Lino searches all text fields on this model.


  .. attribute:: quick_search_fields_digit = None

    As :attr:`quick_search_fields`, but this list is used when the
    search text contains only digits (and does not start with '0').

    If you don't specify it, Lino searches all number fields on this model.


In your model declarations your specify these attributes as a `string`
containing a space-separated list of field names. Lino resolves this `string`
into a `tuple` of data elements during :term:`site startup`.

If you want to not inherit this field from a parent using standard
MRO, then you must set that field explicitly to `None`.

This is also used when a gridfilter has been set on a foreign key column which
points to this model.

For end-user documentation see :term:`quick search field`.

See also :class:`lino.modlib.about.SiteSearch`
