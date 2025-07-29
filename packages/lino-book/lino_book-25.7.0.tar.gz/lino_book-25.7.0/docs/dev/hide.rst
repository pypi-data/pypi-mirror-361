========================
Hide individual fields
========================

.. currentmodule:: lino.core.model

Instead of just disabling a field, you may want to hide it altogether. You do
this either by calling the :meth:`hide_elements` method, or by setting the
:attr:`hidden_elements` attribute on a model or an actor.

Unlike disabling fields, hiding them happens once and for all during site
startup.


.. class:: Model
  :noindex:

  .. method:: hide_elements(self, *names):

    Mark the named data elements (fields) as hidden.  They remain in
    the database but are not visible in the user interface.

  .. attribute:: hidden_elements = frozenset()

    If specified, this is the default value for
    :attr:`hidden_elements <lino.core.tables.AbstractTable.hidden_elements>`
    of every `Table` on this model.

For example the :attr:`hide_region <lino_xl.lib.countries.Plugin.hide_region>`
option of the :mod:`lino_xl.lib.countries` plugin uses this to


.. class:: lino.core.actors.Actor
  :noindex:


  .. attribute:: hidden_elements = frozenset()

    A set of names of layout elements which are hidden by default.

    The default is an empty set except for
    :class:`lino.core.dbtables.Table` where this will be populated from
    :attr:`hidden_elements <lino.core.model.Model.hidden_elements>`
    of the :class:`lino.core.model.Model`.

    Note that these names are not being verified to be names of
    existing fields. This fact is being used by UNION tables like
    :class:`lino_xl.lib.vat.IntracomInvoices`
