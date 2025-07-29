.. include:: /../docs/shared/include/defs.rst

.. _dev.delete:

=============================
Customize delete behaviour
=============================

This topic guide explains how to customize behaviour around deleting records.

Unlike Django, Lino has ``PROTECT`` as the default ``on_delete`` strategy in
`ForeignKey` fields.  If you want ``CASCADE``, then you specify it explicitly
using the :attr:`allow_cascaded_delete
<lino.core.model.Model.allow_cascaded_delete>` attribute on the model whose
instances will be deleted.

The :meth:`disable_delete <lino.core.model.Model.disable_delete>` method of a
model decides whether a given database object may be deleted or not. Also the
:meth:`disable_delete <lino.core.dbtables.Table.disable_delete>` method of an
actor.

The :attr:`disable_delete` item in :attr:`data_record
<lino.core.requests.ValidActionResponses.data_record>` is a "preview" of whether
that row can be deleted or not.  The front end may use this information to
disable or enable its delete button.

But the :class:`DeleteSelected <lino.core.actions.DeleteSelected>` action will
verify again before actually deleting a row.

When Lino analyzes the application's models at startup, it adds a
"disable_delete handler" (:mod:`lino.core.ddh`) to every model.

The :meth:`lino.utils.diag.Analyzer.show_foreign_keys` can help to find examples
for writing tests. It is used in specs like :ref:`noi.specs.ddh` or
:ref:`voga.specs.db_roger`.



.. _lino.tested.ddh:


.. currentmodule:: lino.core.model

The ``disable_delete`` method
=============================

To customize whether a :term:`database row` can be deleted or not, you
override the :meth:`Model.disable_delete` method.

When a user has view and write permission to an actor, they usually also have
permission to delete individual :term:`database rows <database row>` using the
|delete| button in the toolbar.

But before actually deleting a row, Lino calls another hook
the :meth:`disable_delete <Model.disable_delete>` method do decide whether
the action will actually be executed. And you can override this method.

As an example, here is how the :meth:`disable_delete <Model.disable_delete>`
method of :class:`lino_xl.lib.cal.GuestsByEvent` table adds a customized veto
message to refuse deleting the presence of a guest in a :term:`calendar entry`
for which Lino manages presences automatically::

    @classmethod
    def disable_delete(cls, obj, ar):
        msg = super(GuestsByEvent, cls).disable_delete(obj, ar)
        if msg is not None:
            return msg
        mi = ar.master_instance
        assert mi == obj.event
        if mi.can_edit_guests_manually():
            return None
        return _("Cannot edit guests manually.")

When you override this method, be careful to call :func:`super` because Lino
finds a lot of veto reasons automatically for you by checking whether the
database contains related objects. For example. Lino by default forbids to
delete any object that is referenced by other objects. Users will get a message
of type "Cannot delete X because n Ys refer to it". See `About cascaded
deletes`_ below for customizing this behaviour.


About cascaded deletes
======================

Lino changes Django's default behaviour regarding cascaded delete on ForeignKey
fields.  You can set the :attr:`allow_cascaded_copy
<Model.allow_cascaded_delete>` and :attr:`allow_cascaded_copy
<Model.allow_cascaded_copy>` class attributes of a model to customize this
behaviour.

With Lino, unlike plain Django, you control cascaded delete behaviour on the
model whose instances are going to be deleted instead of defining it on the
models that refer to it.
So you usually don't need to care about Django's `on_delete
<https://docs.djangoproject.com/en/5.0/ref/models/fields/#django.db.models.ForeignKey.on_delete>`__
attribute, Lino automatically (in :meth:`kernel_startup
<lino.core.kernel.Kernel.kernel_startup>`) sets this to ``PROTECT`` for all FK
fields that are not listed in the :attr:`allow_cascaded_delete` of their model.

.. class:: Model
  :noindex:

  .. attribute:: allow_cascaded_delete

    A set of names of `ForeignKey` or `GenericForeignKey` fields of
    this model that allow for cascaded delete.

    If this is a simple string, Lino expects it to be a space-separated list of
    field names and convert it into a set at startup.

    This is also used by :class:`lino.mixins.duplicable.Duplicate` to decide
    whether slaves of a record being duplicated should be duplicated as well.

Example: Lino should not refuse to delete a Mail just because it has some
Recipient.  When deleting a Mail, Lino should also delete its Recipients. That's
why :class:`lino_xl.lib.outbox.models.Recipient` has ``allow_cascaded_delete =
'mail'``.


Removing the delete button altogether
=====================================

.. class:: lino.core.actors.Actor
  :noindex:

  .. attribute:: allow_delete = True

    If this is `False`, the table won't have any delete_action.
