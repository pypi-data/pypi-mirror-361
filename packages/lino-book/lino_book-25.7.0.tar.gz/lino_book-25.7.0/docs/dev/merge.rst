.. doctest docs/dev/merge.rst

=================================
Customize how data is merged
=================================

There are many ways to customize how to find duplicate database rows and to
merge them.


.. currentmodule:: lino.core.merge

.. class:: MergeAction

  Implements the :attr:`lino.core.model.Model.merge_row` action.

  This action has a dynamically generated parameters window.

.. currentmodule:: lino.core.model

.. class:: Model
  :noindex:

  .. attribute:: allow_merge_action = False

    Whether this model should have a merge action.

  .. attribute:: merge_row

    Merge this object into another object of same class.

    This action is automatically installed on every model that has
    :attr:`allow_merge_action <lino.core.model.Model.allow_merge_action>` set to
    `True`.

    For example it should not be used on models that have MTI children.


.. class:: lino.core.actors.Actor
  :noindex:
