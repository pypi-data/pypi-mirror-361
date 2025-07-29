.. doctest docs/dev/disable.rst

========================================
Disable elements of the user interface
========================================

Lino provides several methods to customize whether data is editable or not.

.. _disabled_fields:

Disable individual fields
================================

.. currentmodule:: lino.core.model

Sometimes you want to disable (make non-editable) individual fields of a form
based on certain conditions.  The conditions for disabling individual fields can
be application specific and based e.g. on user roles or the values of certain
other fields of the object being displayed.

For example, in :ref:`cosi` an invoice disables most fields when it has been
registered.  Here are two screenshots of a same invoice, once when the invoice's
state is "draft" and once when it is "registered":

.. image:: /apps/cosi/sales.Invoice.detail.draft.png
    :scale: 20

.. image:: /apps/cosi/sales.Invoice.detail.registered.png
    :scale: 20

In Lino you define this behaviour by overriding the :meth:`disabled_fields
<lino.core.model.Model.disabled_fields>` instance method on your model.

.. class:: Model
  :noindex:

  .. method:: disabled_fields(self, ar)

    Return a set of field names that should be *disabled* (i.e. not editable)
    for this :term:`database object`.

Here is a fictive example::

    class MyModel(dd.Model):
        ...
        def disabled_fields(self, ar):
            s = super(MyModel, self).disabled_fields(ar)
            ...
            return set()

The :class:`Invoice` model used in above screenshots does something
like this::

    class Invoice(dd.Model):
      ...
      def disabled_fields(self, ar):
          df = super(Invoice, self).disabled_fields(ar)
          if self.state == InvoiceStates.registered:
              df.add('subject')
              df.add('payment_term')
              ...
          return df

The decision which fields to disable may depend an the current user. Here is a
fictive example of a model :class:`Case` where only the author may change first
and last name::

    class Case(dd.Model):
      ...
      def disabled_fields(self, ar):
          df = super(Case, self).disabled_fields(ar)
          if self.author == ar.get_user():
              return df
          df.add('first_name')
          df.add('last_name')
          return df


You may want to override this method on the actor instead of per model. In that
case it must be a `classmethod` with two arguments `obj` and `ar`::

  @classmethod
  def disabled_fields(cls, obj, ar):
      s = super(MyActor, cls).disabled_fields(obj, ar)
      ...
      return set()

Note that Lino calls the :meth:`disabled_fields <Model.disabled_fields>` method
only once per :term:`database row` and request.  The returned set is cached in
memory.

Disable actions
=================

You may also disable *actions* simply by adding their name to the set returned
by  :meth:`disabled_fields <lino.core.model.Model.disabled_fields>`. (The method
name :meth:`disabled_fields` is actually misleading, one day we might rename it
to :meth:`disabled_elements`).



.. _dev.actor_config.editing:

Disable editing of a whole table
================================

In some :term:`data windows <data window>` you may want to disable editing
functionality altogether.

For example :class:`lino.modlib.changes.Changes` or
:class:`lino.modlib.checkdata.Messages`. You don't want to modify them, nor
delete them, not create new rows in these data windows. Not even when you are a
:term:`site manager`.

You do this by setting :attr:`Actor.editable` to `False`. This will remove
editing functionality for everybody.


Disable editing of a whole table
================================

In other cases you want to remove editing functionality only for certain user
types.  You do this by overriding the :meth:`Actor.hide_editing` method.  For
example :class:`lino_xl.lib.products.Products` says that ProductsUser can see
products, but only ProductsStaff can edit them::

  class Products(dd.Table):

    required_roles = dd.login_required(ProductsUser)

    @classmethod
    def hide_editing(cls, user_type):
        if user_type is not None:
            if not user_type.has_required_roles([ProductsStaff]):
                return True
        return super(Products, cls).hide_editing(user_type)


.. class:: lino.core.actors.Actor
  :noindex:

  .. attribute:: editable

    Whether a :term:`data window` on this actor is editable.

    The :term:`front end` uses this information to generate optimized JS code
    for these actors.

    When this is `False`, Lino won't even call :meth:`get_view_permission` for
    actions that are not :attr:`readonly <lino.core.actions.Action.readonly>`.

    Set this explicitly to `True` or `False` to make the whole actor editable or
    not.  Otherwise Lino will guess what you want during startup and set it to
    `False` if the actor is a Table and has a `get_data_rows` method (which
    usually means that it is a virtual table), otherwise to `True`.

    This attribute is not inherited to subclasses.


.. currentmodule:: lino.core.actors
.. _dev.actor_config.hide_navigator:

How to remove the navigation buttons
====================================

TODO: This section does not yet reflect the new
:attr:`dd.Actor.default_record_id` attribute (which automatically disables
navigation).

In some :term:`data windows <data window>` you may want to disable navigation
functionality altogether by setting :attr:`hide_navigator
<Actor.hide_navigator>` to True.

For example the :class:`lino.modlib.users.Users` actor shows all :term:`user
accounts <user account>` and defines a :term:`detail layout` to edit their data
fields. But this table must of course be visible only to a :term:`site manager`.
In order to give normal users a chance to see and edit at least their own
:term:`user settings`, we have the :class:`lino.modlib.users.MySettings`
actor. It inherits from :class:`lino.modlib.users.Users`, but instead of showing
a list of them, it jumps directly to the detail window of the current user. So
we set the default action to "detail". And of course we don't want the user to
be able to navigate to their fellow users. So we disable navigation::

  class MySettings(Users):
      hide_navigator = True
      allow_create = False
      allow_delete = False

      @classmethod
      def get_default_action(cls):
          return cls.detail_action


Or the :class:`lino.modlib.system.SiteConfig` object (a :term:`database model`
for which there is always exactly one instance in a given database). To edit it,
we use the following :term:`data table`::

  class SiteConfigs(dd.Table):

      model = 'system.SiteConfig'
      hide_navigator = True

      detail_layout = """
      default_build_method
      """

      @classmethod
      def get_default_action(cls):
          return cls.detail_action

Or a :term:`shopping cart` is done like this::

  class MyCart(My, Carts):
      hide_navigator = True

.. _dev.actor_config.hide_top_toolbar:

Actors with a modified toolbar
==============================

The :attr:`hide_top_toolbar <Actor.hide_top_toolbar>` attribute changes the
toolbar (1) to be at the bottom of the window instead of the top and (2) to have
only actor-specific actions, i.e. no navigation buttons, no refresh button, no
displayText area.

This attribute is used only with :term:`ExtJS front end`. In React it is
ignored. For example :class:`lino.modlib.system.SiteConfigs` does this::

  class SiteConfigs(dd.Table):
      hide_top_toolbar = True

(TODO: rename it to something else.)
