==================
The front end
==================

(Needs revision. See also :doc:`/dev/rendering`.)

Lino comes with an extensible collection of out-of-the-box front ends.

Currently there's one serious front end based on Sencha ExtJS and
and another, experimental and more lightweight, based on the
Twitter/Bootstrap library.

.. _lino.ui.renderer:

UI renderer
===========

Lino has an extensible set of front ends (UIs).  This means that
you may access your Lino application in different ways.  Currently
there is only one fully functional UI, the
:ref:`lino.ui.extjs`.

But also the :ref:`lino.ui.plain` can be useful.  You can currently
see it in action by clicking the "HTML" button of a Grid.

.. _lino.ui.extjs:

ExtJS UI
--------

.. _lino.ui.plain:

Plain UI
--------

A "plain" HTML render that uses bootstrap and jQuery.
It is called "plain" because it's much more lightweight 
than the :ref:`lino.ui.extjs`.


.. _lino.ui.grid:

Grid
====

.. _lino.ui.detail:

Detail
======

The detail view is when you see only one row at a time. 


.. _lino.ui.detail.Save:

Save
----

Click this button to save your changes in the form.



