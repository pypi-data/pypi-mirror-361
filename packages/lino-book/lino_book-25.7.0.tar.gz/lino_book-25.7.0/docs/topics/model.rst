.. doctest docs/topics/models.rst

.. _dg.topics.models:

===================
The ``Model`` class
===================

.. contents::
    :depth: 1
    :local:


Lino extends the Django model
=============================

.. currentmodule:: lino.core.model

.. class:: Model

  Lino extension of Django's :term:`database model`. This is a subclass of
  Django's `Model <https://docs.djangoproject.com/en/5.0/ref/models/class/>`_
  class (:class:`django.db.models.Model`).

  In a Lino application you will define your models as direct or indirect
  subclasses of :class:`lino.core.model.Model` (usually referred as
  :class:`dd.Model`).

  When a Lino application imports plain Django Model classes, Lino will "extend"
  these by adding the attributes and methods defined here to these classes.

  .. rubric:: Virtual fields

  .. attribute:: overview

    A multi-paragraph representation of this :term:`database row`.

    Customizable using :meth:`get_overview_elems`.

  .. attribute:: navigation_panel

    A virtual field that displays the **navigation panel** for this row.  This
    may be included in a detail layout, usually either on the left or the right
    side with full height.

  .. rubric:: Workflow

  .. attribute:: workflow_buttons

    Shows the current *workflow state* of this :term:`database row` and a list
    of available *workflow actions*.

  .. attribute:: workflow_state_field

    Optional default value for the :attr:`workflow_state_field
    <lino.core.table.Table.workflow_state_field>` of all :term:`data tables
    <data table>` based on this model.

  .. attribute:: workflow_owner_field

    Optional default value for :attr:`workflow_owner_field
    <lino.core.table.Table.workflow_owner_field>` on all :term:`data tables
    <data table>` based on this model.



Field-specific customization hooks
==================================

You can optionally define some field-specific customization hooks. `FOO` in this
section is the name of a database field defined on the same model (or on a
parent).

.. class:: Model
  :noindex:

  .. method:: FOO_changed

    Called when field FOO of an instance of this model has been
    modified through the user interface.

    Example::

      def city_changed(self, ar):
          print("User {} changed city of {} to {}!".format(
              ar.get_user(), self, self.city))

    Note: If you want to know the old value when reacting to a change,
    consider writing :meth:`Model.after_ui_save` instead.

  .. method:: FOO_choices

    Return a queryset or list of allowed choices for field FOO.

    For every field named "FOO", if the model has a method called
    "FOO_choices" (which must be decorated by :func:`dd.chooser`),
    then this method will be installed as a chooser for this
    field.

    Example of a context-sensitive chooser method::

      country = dd.ForeignKey(
          'countries.Country', blank=True, null=True)
      city = dd.ForeignKey(
          'countries.City', blank=True, null=True)

      @chooser()
      def city_choices(cls,country):
          if country is not None:
              return country.place_set.order_by('name')
          return cls.city.field.remote_field.model.objects.order_by('name')


  .. method:: create_FOO_choice

    For every field named "FOO" for which a chooser exists, if the model
    also has a method called "create_FOO_choice", then this chooser will be
    a :term:`learning chooser`. That is, users can enter text into the
    combobox, and Lino will create a new database object from it.

    This works only if FOO is (1) a foreign key and (2) has a chooser.
    See also :term:`learning foreign key`.

  .. method:: get_choices_text(self, request, actor, field)

    Return the text to be displayed when an instance of this model
    is being used as a choice in a combobox of a ForeignKey field
    pointing to this model.
    `request` is the web request,
    `actor` is the requesting actor.

    The default behaviour is to simply return `str(self)`.

    A usage example is :class:`lino_xl.lib.countries.Place`.


  .. method:: disable_delete(self, ar=None)

    Decide whether this :term:`database object` may be deleted.     Return
    `None` when there is no veto against deleting this :term:`database row`,
    otherwise a translatable message that explains to the user why they can't
    delete this row.

    The argument `ar` contains the :term:`action request` that is trying to
    delete. `ar` is possibly `None` when this is being called from a script or
    batch process.

    The default behaviour checks whether there are any related objects which would
    not get cascade-deleted and thus produce a database integrity error.

    You can override this method e.g. for defining additional conditions.
    Example::

      def disable_delete(self, ar=None):
          msg = super(MyModel, self).disable_delete(ar)
          if msg is not None:
              return msg
          if self.is_imported:
              return _("Cannot delete imported records.")

    When overriding, be careful to not skip the `super` method unless you know
    what you want.

    Note that :class:`lino.mixins.polymorphic.Polymorphic` overrides this.

  .. method:: update_field

    Shortcut to call :func:`lino.core.inject.update_field` for usage during
    :meth:`lino.core.site.Site.do_site_startup` in a :xfile:`settings.py` or
    similar place.

    See :ref:`dg.projects.cosi3.settings`.


How your model behaves in regard to other models:

- :attr:`Model.allow_cascaded_copy`
- :attr:`Model.allow_cascaded_delete`

Customize what happens when an instance is created:

- :meth:`Model.submit_insert`
- :meth:`Model.on_create`
- :meth:`Model.before_ui_save`
- :meth:`Model.after_ui_save`
- :meth:`Model.after_ui_create`
- :meth:`Model.get_row_permission`

Some methods you will use but not override:

- :attr:`Model.get_data_elem`
- :attr:`Model.add_param_filter`
- :attr:`Model.define_action`
- :attr:`Model.hide_elements`
