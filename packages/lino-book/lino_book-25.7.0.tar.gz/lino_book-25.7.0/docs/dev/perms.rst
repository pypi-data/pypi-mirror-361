.. doctest docs/dev/perms.rst
.. _dev.permissions:
.. _permissions:

===========================
Introduction to permissions
===========================

As soon as a database application is used by more than one user, we usually need
to speak about **permissions**.  For example, a :term:`site manager` can
see certain resources that a simple :term:`end user` should not get to see.  The
application must check whether a given user has permission to see a given
resource or to execute a given action.  An application framework must provide a
system for managing these permissions. Lino replaces Django's user management
and permission system (see :doc:`/dev/about/auth` if you wonder why).

.. contents::
    :depth: 1
    :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino import startup
>>> startup('lino_book.projects.min9.settings')
>>> from lino.api.doctest import *


User roles
==========

The basic unit for defining permissions in Lino are called :term:`user role`.

.. glossary::

  user role

    A responsibility that can be given to a user of a Lino application, and
    which grants permission to access certain functionalities of the
    application.

Every user (even :class:`AnonymousUser`) has a :term:`user role` assigned to them.
Every :term:`action` on a :term:`data table` has a set of *required* roles.

.. currentmodule:: lino.core.roles

Lino comes with a few built-in user roles that are defined in
:mod:`lino.core.roles`.

A user role can inherit from one or several other user roles.
For example, the
:class:`SiteAdmin` role inherits from :class:`SiteStaff`, :class:`Supervisor`
and :class:`Explorer`.

Plugins may define their own user roles that are subclasses of these builtin
roles.

A real-world application can define *many* user roles. For example here is an
inheritance diagram of the roles used by :ref:`cosi`:

.. inheritance-diagram:: lino_cosi.lib.cosi.user_types

And if you think this diagram is complex, then don't look at the following one
(that of :ref:`noi`)...

.. inheritance-diagram:: lino_noi.lib.noi.user_types

.. And we won't even show the one of :ref:`welfare`)
.. .. inheritance-diagram:: lino_welfare.modlib.welfare.user_types


Defining required roles
=======================

The :term:`application developer` specifies which roles are **required** for a
given resource.

For example, the :class:`users.Users <lino.modlib.users.Users>` table
is visible only for users
who have the :class:`SiteAdmin <lino.core.roles.SiteAdmin>` role:

>>> users.Users.required_roles
{<class 'lino.core.roles.SiteAdmin'>}

Rather than setting :attr:`required_roles
<lino.modlib.users.Users.required_roles>` directly, we recommend to use the
:func:`login_required` function for specifying required roles, so the definition
of the :class:`Users` table is actually::

  class Users(dd.Table):
      ...
      required_roles = dd.login_required(SiteAdmin)

More precisely, "resource" is one of the following:

- an actor (a subclass of :class:`lino.core.actors.Actor`)
- an action (an instance of :class:`lino.core.actions.Action` or a
  subclass thereof)
- a panel (an instance of :class:`lino.core.layouts.Panel`)

These objects have a :attr:`required_roles
<lino.core.permissions.Permittable.required_roles>` attribute, which must be a
:func:`set` of the user roles required for getting permission to access this
resource.

This set of user roles can be specified using the :func:`login_required
<lino.core.roles.login_required>` utility function.  You can also specify it
manually. But it must satisfy some conditions described in
:func:`check_required_roles <lino.core.roles.check_required_roles>`.

See :meth:`lino.modlib.users.UserType.has_required_role`

>>> from lino.core.roles import SiteUser, SiteAdmin
>>> user = SiteUser()
>>> admin = SiteAdmin()
>>> user.has_required_roles(rt.models.users.Users.required_roles)
False
>>> admin.has_required_roles(rt.models.users.Users.required_roles)
True

>>> robin = users.User.objects.get(username="robin")
>>> robin.has_required_roles({SiteAdmin})
True


User types
==========

When creating a new user, the :term:`site manager` needs to assign these roles
to every user. But imagine they would have to fill out, for each user group, a
multiple-choice combobox with all available roles from above examples! They
would get crazy!

That's why we have :term:`user types <user type>`.

.. glossary::

  user type

    Each user type is basically not much more than a *name* and a
    storable *value* given to a selected :term:`user role`.


Here is the default list of user types, defined in :mod:`lino.core.user_types`:

>>> rt.show(users.UserTypes)
======= =========== ===============
 value   name        text
------- ----------- ---------------
 000     anonymous   Anonymous
 100     user        User
 900     admin       Administrator
======= =========== ===============
<BLANKLINE>

Every :term:`user account` has a :term:`user type`, stored in the
:attr:`user_type <lino.modlib.users.User.user_type>` field of the
:class:`users.User <lino.modlib.users.User>` model. (If that field is empty, the
user account is "inactive" and can't be used for signing in).

>>> rt.show('users.AllUsers', column_names="username user_type")
========== =====================
 Username   User type
---------- ---------------------
 robin      900 (Administrator)
 rolf       900 (Administrator)
 romain     900 (Administrator)
========== =====================
<BLANKLINE>

The application developer defines the user types for their application by
populating the :class:`UserTypes <lino.modlib.users.choicelists.UserTypes>`
choicelist.

User types are a meaningful *subset of all available combinations of roles*
a way to classify end users in order to grant them different sets
of permissions.

Actually a user *type* contains a bit more information than a user
*role*.  It has the following fields:

- :attr:`role`, the role given to users of this type
- :attr:`text`, a translatable name
- :attr:`value`, a value for storing it in the database

- :attr:`readonly
  <lino.modlib.users.choicelists.UserType.readonly>` defines a user
  type which shows everything that a given user role can see, but
  unlike the original user role it cannot change any data.

- :attr:`hidden_languages
  <lino.modlib.users.choicelists.UserType.hidden_languages>` may optionally
  specify a set of languages to *not* show to users of this type. This is used
  on sites with more than three or four :attr:`languages
  <lino.core.site.Site.languages>`.



The user types module
========================

The :attr:`roles_required
<lino.core.permissions.Permittable.roles_required>` attribute is being
ignored when :attr:`user_types_module
<lino.core.site.Site.user_types_module>` is empty.


.. xfile:: roles.py

.. xfile:: user_types.py

The :xfile:`roles.py` is used for both defining roles

A :xfile:`user_types.py` module is used for defining the user roles
that we want to make available in a given application.  Every user
type is assigned to one and only one user role. But not every user
role is made available for selection in that list.






Relation between user roles and user types
==========================================

There is a built-in virtual table that shows an overview of which roles are
contained for each user type.  This table can be helpful for documenting the
permissions granted to each user type.

>>> rt.show(users.UserRoles)
======================== ===== ===== =====
 Name                     000   100   900
------------------------ ----- ----- -----
 cal.GuestOperator              ☑     ☑
 comments.CommentsStaff               ☑
 comments.CommentsUser          ☑     ☑
 contacts.ContactsStaff               ☑
 contacts.ContactsUser          ☑     ☑
 excerpts.ExcerptsStaff               ☑
 excerpts.ExcerptsUser          ☑     ☑
 notes.NotesStaff                     ☑
 notes.NotesUser                ☑     ☑
 office.OfficeStaff                   ☑
 office.OfficeUser              ☑     ☑
 polls.PollsAdmin                     ☑
 polls.PollsUser                ☑     ☑
 xl.SiteAdmin                         ☑
 xl.SiteUser                    ☑
======================== ===== ===== =====
<BLANKLINE>

Accessing permissions from within your code
===========================================

Just some examples...

The following two lines are equivalent. It's a matter of taste and sometimes of
context which one you choose:

>>> UserTypes = rt.models.users.UserTypes
>>> from lino.modlib.users.choicelists import UserTypes

>>> UserTypes.admin
<users.UserTypes.admin:900>

>>> UserTypes.admin.role  #doctest: +ELLIPSIS
<lino_xl.lib.xl.user_types.SiteAdmin object at ...>


>>> UserTypes.admin.readonly
False

>>> UserTypes.admin.hidden_languages


>>> robin = users.User.objects.get(username='robin')
>>> robin.user_type  #doctest: +ELLIPSIS
<users.UserTypes.admin:900>

>>> robin.user_type.role  #doctest: +ELLIPSIS
<lino_xl.lib.xl.user_types.SiteAdmin object at ...>





Local customizations
====================

You may have noted that :class:`UserTypes
<lino.modlib.users.choicelists.UserTypes>` is a choicelist, not a
database table.  This is because it depends on the application and is
usually not locally modified.

Local site managers may nevertheless decide to change the set of
available user types.


.. _debug_permissions:

Permission debug messages
=========================

Sometimes you want to know why a given action is available (or not
available) on an actor where you would not (or would) have expected it
to be.

In this situation you can temporarily set the `debug_permissions`
attributes on both the :attr:`Actor <lino.core.actors.Actor.debug_permissions>` and
the :attr:`Action <lino.core.actions.Action.debug_permissions>` to True.

This will cause Lino to log an info message for each invocation of a
handler on this action.

Since you probably don't want to have this feature accidentally
activated on a production server, Lino will raise an Exception if this
happens when :setting:`DEBUG` is False.
