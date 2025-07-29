.. doctest docs/dev/create.rst

=================================
Customize how data is created
=================================

Lino provides several ways for customizing how to insert rows into the database.

You can set an actor's :attr:`allow_create
<lino.core.actors.Actor.allow_create>` to `False` in order to disable the insert
action (without disable other editing, which you would do by setting
:attr:`readonly <lino.core.actors.Actor.readonly>` to True). For example:

- :class:`lino.modlib.comments.RecentComments`
- :class:`lino_xl.lib.invoicing.ItemsByPlan`

You can write a customized insert action. For example:

- :class:`lino.modlib.users.CreateAccount`
- :class:`lino_prima.lib.school.CreateExamByCourse`


.. currentmodule:: lino.core.model

.. class:: Model
  :noindex:

  .. classmethod:: disable_create(self, ar)

    Return a veto message if you want to refuse creating rows on this model in
    the given action request even when permission has been given.

    The default implementation returns `None`, which means that there is no
    veto.

    The :class:`lino_xl.lib.accounting.VoucherItem` mixin uses this to disable
    creating new items in a registered voucher.

  .. method:: on_create(self)

    Override this to set default values that depend on the request.

    The difference with Django's `pre_init
    <https://docs.djangoproject.com/en/5.0/ref/signals/#pre-init>`__
    and `post_init
    <https://docs.djangoproject.com/en/5.0/ref/signals/#post-init>`__
    signals is that (1) you override the method instead of binding
    a signal and (2) you get the action request as argument.

    Used e.g. by :class:`lino_xl.lib.notes.Note`.

  .. method:: after_ui_create(self, ar)

    Hook to define custom behaviour to run when a user has created a new instance
    of this model.


  .. attribute:: submit_insert

    The :class:`SubmitInsert <lino.core.actions.SubmitInsert>` action to be
    executed when the when the users submits an insert window.

    See :mod:`lino.mixins.dupable` for an example of how to override it.

  .. method:: create_from_choice(cls, text)

    Called when a learning combo has been submitted.
    Create a persistent database object if the given text contains enough information.

  .. method:: choice_text_to_dict(cls, text)

    Return a dict of the fields to fill when the given text contains enough
    information for creating a new database object.


.. class:: lino.core.actors.Actor
  :noindex:

  .. attribute:: allow_create

    If this is False, the table won't have any insert_action.


  .. classmethod:: get_create_permission(self, ar)

    Dynamic test per request.

    This is being called only when :attr:`allow_create` is True.

  .. classmethod:: get_insert_action(cls)

    Create a new instance for each actor because :meth:`attach_to_actor` will
    modify the :attr:`help_text`
