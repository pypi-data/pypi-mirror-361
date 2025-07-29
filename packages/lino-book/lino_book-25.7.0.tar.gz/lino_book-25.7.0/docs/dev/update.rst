.. doctest docs/dev/update.rst

=================================
Customize how data is updated
=================================

There are many ways to customize how to update rows in the database.

.. currentmodule:: lino.core.model

.. class:: Model
  :noindex:

  .. method:: before_ui_save(self, ar, cw)

    A hook for adding custom code to be executed each time an
    instance of this model gets updated via the user interface and
    **before** the changes are written to the database.

    Consider using the :data:`pre_ui_save
    <lino.core.signals.pre_ui_save>` signal instead.

    Example in :class:`lino_xl.lib.cal.Event` to mark the
    event as user modified by setting a default state.

  .. method:: after_ui_save(self, ar, cw)

    Like :meth:`before_ui_save`, but is called **after** the changes are written
    to the database.

    Arguments:

        ``ar``: the :term:`action request`.

        ``cw``: the :class:`ChangeWatcher <lino.core.diff.ChangeWatcher>`
        object, or `None` if this is a new instance.

    Called after a PUT or POST on this row, and after the row has been saved.

    Used by
    :class:`lino_welfare.modlib.debts.models.Budget`
    to fill default entries to a new Budget,
    or by :class:`lino_welfare.modlib.cbss.models.CBSSRequest`
    to execute the request,
    or by
    :class:`lino_welfare.modlib.jobs.models.Contract`,
    :class:`lino_welfare.modlib.pcsw.models.Coaching` or
    :class:`lino.modlib.vat.models.Vat`.
    Or :class:`lino_welfare.modlib.households.models.Household`
    overrides this in order to call its `populate` method.

  .. method:: update_owned_instance(self, controllable)

    Called by :class:`lino.modlib.gfks.Controllable`.

  .. method:: after_update_owned_instance(self, controllable)

    Called by :class:`lino.modlib.gfks.Controllable`.



.. class:: lino.core.actors.Actor
  :noindex:
