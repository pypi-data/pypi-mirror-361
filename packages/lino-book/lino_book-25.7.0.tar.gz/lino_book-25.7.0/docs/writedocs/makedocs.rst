.. doctest docs/writedocs/makedocs.rst
.. _dg.topics.makedocs:

======================
About local help pages
======================

The :manage:`makehelp` command generates the :term:`local help pages` of a
:term:`Lino site`, that is, a set of static html pages in your
:file:`/media/cache/help` directory (from where your web server will serve
them). These pages are Lino's answer to clicking on the :guilabel:`?` button.

The :term:`local help pages` system is based on a few conventions.

Database models and data tables are documented as ``autodoc`` directives using
:term:`simplified naming`.

.. glossary::

  simplified naming

    The convention to document everything in the global name space of the
    :xfile:`models.py` file of a plugin without the submodule that implements
    it.

    For example when we say
    :class:`lino.modlib.users.User`,
    :class:`lino.modlib.users.Users` or
    :class:`lino.modlib.users.UserTypes`,
    then we ignore the face that these classes are actually defined in
    different modules.


The local help pages make heavy use of intersphinx to refer to other
documentation websites.  That's why :manage:`makehelp` requires these other
websites to be online when building the local docs.

For every plugin of an application, the developer must provide a
:rst:role:`ref` target with end-user documentation about this plugin.




.. include:: /../docs/shared/include/tested.rst

>>> import lino
>>> lino.startup('lino_book.projects.min1.settings')
>>> from lino.api.doctest import *

>>> rt.models.users.User
<class 'lino.modlib.users.models.User'>

>>> rt.models.users.Users
lino.modlib.users.ui.Users

>>> rt.models.users.UserTypes
lino.modlib.users.choicelists.UserTypes
