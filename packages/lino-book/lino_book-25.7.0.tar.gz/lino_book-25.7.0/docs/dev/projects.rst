=============
Demo projects
=============

Introduction see :doc:`/discover`.

An overview of available demo projects is given in :mod:`lino_book.projects` and
in :ref:`book.specs.projects` (we are working on merging these two documents).

You can initialize all demo projects in one operation by running :cmd:`inv prep`
from within the root directory of your ``book`` repository::

    $ go book
    $ inv prep

This will run :cmd:`pm prep` in all demo projects.

The list of demo projects included with a code repository is defined in the
:envvar:`demo_projects` setting of the :xfile:`tasks.py` file.
