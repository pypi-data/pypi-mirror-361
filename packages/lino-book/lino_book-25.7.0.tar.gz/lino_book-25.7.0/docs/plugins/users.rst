.. doctest docs/plugins/users.rst
.. _specs.users:
.. _dg.plugins.users:

===========================
``users`` : user management
===========================

.. currentmodule:: lino.modlib.users

This document describes the :mod:`lino.modlib.users` plugin, which in Lino
replaces :mod:`django.contrib.auth`. See also :doc:`/dev/users` for getting
started with user management. If you wonder why Lino replaces Django's user
management and permission system, see :doc:`/dev/about/auth`.


.. contents::
  :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.noi1r.startup import *



Menu entries
============

This plugin adds the following menu entries:

- :menuselection:`Site --> User sessions`
- :menuselection:`Configure --> System --> Users`
- :menuselection:`Explorer --> System --> Authorities`
- :menuselection:`Explorer --> System --> User roles`
- :menuselection:`Explorer --> System --> User types`


Users
=====

.. class:: User

    The Django model used to represent a :term:`user account`.

    .. rubric:: Database fields that must be edited by a :term:`site manager`:

    .. attribute:: username

        Must be either unique or empty.  User accounts having this field empty
        cannot be used to sign in.

    .. attribute:: user_type

        The :term:`user type` assigned to this user. User accounts having this
        field empty cannot be used to sign in.

        See also :doc:`/dev/perms`.

    .. attribute:: partner

        The :term:`partner` record with additional contact information about
        this user account.

        This field is used to optionally link a :term:`user account` to a
        :term:`partner`.  Some applications provide functionalities that aren't
        available unless this field is given.

        A same partner can have more than one user accounts.

        This is a pointer to :class:`lino_xl.lib.contacts.Partner`. This is a
        :class:`DummyField` when :mod:`lino_xl.lib.contacts` is not installed or
        when User is a subclass of :class:`Partner
        <lino_xl.lib.contacts.Partner>` .


    .. rubric:: Database fields that can be edited by the user as their :term:`user settings`:

    .. attribute:: nickname

        The nickname  used to refer to you when speaking to
        other :term:`site users <site user>`.
        Does not need to be unique but should be reasonably identifying.

        This field is hidden unless :setting:`users.with_nickname` is `True`.
        See also :meth:`__str__` and :meth:`get_full_name`.


    .. attribute:: initials

        The initials used to refer to you when speaking to
        :term:`business partners <business partner>`.
        Does not need to be unique but should be reasonably identifying.

    .. attribute:: time_zone

        The :term:`time zone` Lino should use in time fields or when displaying
        timestamps to this user.

    .. attribute:: date_format

        The date format to use when parsing or displaying dates.

        See :class:`lino.modlib.about.DateFormats`.

    Database fields that aren't directly editable:

    .. attribute:: verification_code

        A random string that has been sent to the user via email in order to
        verify their email address.

        When this is non empty, :meth:`is_verified` returns `False` and the
        :attr:`verify_me` action is available.

    .. attribute:: verification_password

        A not-yet-active password given by anonymous when they asked for a
        password reset. This will become the active password when the user
        verifies.

    .. attribute:: person

        A virtual read-only field that returns the :class:`Person
        <lino_xl.lib.contacts.Person>` MTI child of the :attr:`partner` (if it
        exists) and otherwise `None`.

    .. attribute:: company

        A virtual read-only field that returns the :class:`Company
        <lino_xl.lib.contacts.Company>` MTI child of the :attr:`partner` (if it
        exists) and otherwise `None`.

    .. attribute:: last_login

        Not used in Lino.

    .. attribute:: end_date
    .. attribute:: start_date

        If :attr:`start_date` is given, then the user cannot sign in
        before that date.  If :attr:`end_date` is given, then the user
        cannot sign in after that date.

        These fields are also used for :doc:`userstats`.

    Instance attributes:

    .. attribute:: authenticated

        No longer used. See as :attr:`is_authenticated`.

    .. attribute:: is_authenticated

        This is always `True`.  Compare with
        :attr:`AnonymousUser.is_authenticated
        <lino.modlib.users.utils.AnonymousUser.authenticated>`.

    .. rubric:: Querying users:

    .. classmethod:: get_active_users(cls, required_roles=None)

      Return a queryset of users that satisfy the specified criteria.

      Usage examples see `Querying users`_ below.

    .. rubric:: Other methods

    .. method:: __str__(self)

      Returns :attr:`nickname` if this field is not empty, otherwise
      :meth:`get_full_name` unless

    .. method:: get_full_name(self)

      Return the user's full name, i.e. :attr:`first_name` followed by
      :attr:`last_name`. If both fields are empty, return the :attr:`initials`
      or the :attr:`username`.

    .. method:: get_row_permission(self, ar, state, ba)

        Only system managers may edit other users.
        See also :meth:`disabled_fields`.

        One exception is when AnonymousUser is not readonly. This
        means that we want to enable online registration. In this case
        everybody can modify an unsaved user.

    .. rubric:: Actions

    .. attribute:: change_password

      Ask for a new password to be used for authentication.

      See :class:`ChangePassword`.

    .. attribute:: verify_me

      Ask for the verification code you have received by email and mark your
      email address as verified.


Data tables
===========

.. class:: Users

    Base class for all data tables on :class:`User`.

.. class:: AllUsers

    Shows the list of all users on this site.

.. class:: UsersOverview

    A variant of :class:`Users` showing only active users and only some
    fields.  This is used on demo sites in :xfile:`admin_main.html` to
    display the list of available users.



User types
==========

>>> rt.show('users.UserTypes', language="en")
======= =============== ===============
 value   name            text
------- --------------- ---------------
 000     anonymous       Anonymous
 100     customer user   Customer
 200     contributor     Contributor
 400     developer       Developer
 900     admin           Administrator
======= =============== ===============
<BLANKLINE>


.. class:: UserTypes

    The list of :term:`user types <user type>` available in this application.

    Every application should define at least three named user types:

    .. attribute:: anonymous

    .. attribute:: user

    .. attribute:: admin

    Class attributes:

    .. attribute:: user_role

      The user role of users having this type.

    .. attribute:: hidden_languages

      Default value for the :attr:`hidden_languages <UserType.hidden_languages>`
      of newly added choice items.

    .. classmethod:: get_anonymous_user(cls)

      Return an instance of :class:`AnonymousUser`.


.. class:: UserType

    An item of the :class:`UserTypes` list. Every instance of this represents a
    :term:`user type`.

    .. attribute:: role

        The role of users having this type. This is an instance of
        :class:`UserRole <lino.core.roles.UserRole>` or some subclass thereof.

    .. attribute:: readonly

        Whether users of this type get only write-proteced access.

    .. attribute:: hidden_languages

        A subset of :attr:`languages<lino.core.site.Site.languages>`
        which should be hidden for users of this type.  Default value
        is :attr:`hidden_languages<UserTypes.hidden_languages>`.  This
        is used on multilingual sites with more than 4 or 5 languages.

    .. method:: context(self)

        Return a context manager so you can write code to be run with
        this as `the current user type`_::

          with UserTypes.admin.context():
              # some code

    .. attribute:: mask_message_types

        A set of notification message types to be masked for users of this type.

        Notifications will not be forwarded to users whose :term:`user type`
        filters them away.


    .. method:: mask_notifications(self, *args)

        Add the given notification message types to the notification mask.


    .. method:: has_required_roles(self, required_roles)

        Return `True` if this user type's :attr:`role` satisfies the specified
        requirements.

    .. method:: find_menu_item(self, bound_action)

        Find the item of the main menu for the specified bound action.




User roles and their usage
==========================

.. class:: UserRoles

Shows a list of the user roles used in this application together with the user
type that have them.

This table can help when designing the list of user types and what permissions
each of them should have.

Example:

>>> rt.show(users.UserRoles)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
================================ ===== ===== ===== ===== =====
 Name                             000   100   200   400   900
-------------------------------- ----- ----- ----- ----- -----
 accounting.LedgerStaff                                   ☑
 blogs.BlogsReader                      ☑     ☑     ☑     ☑
 cal.CalendarReader               ☑
 checkdata.CheckdataUser                      ☑     ☑     ☑
 comments.CommentsReader          ☑     ☑     ☑     ☑     ☑
 comments.CommentsStaff                             ☑     ☑
 comments.CommentsUser                  ☑     ☑     ☑     ☑
 comments.PrivateCommentsReader                     ☑     ☑
 contacts.ContactsStaff                                   ☑
 contacts.ContactsUser                              ☑     ☑
 core.DataExporter                      ☑     ☑     ☑     ☑
 core.Expert                                        ☑     ☑
 core.SiteUser                          ☑     ☑     ☑     ☑
 courses.CoursesUser                          ☑     ☑     ☑
 excerpts.ExcerptsStaff                             ☑     ☑
 excerpts.ExcerptsUser                        ☑     ☑     ☑
 invoicing.InvoicingStaff                                 ☑
 invoicing.InvoicingUser                                  ☑
 noi.Anonymous                    ☑
 noi.Contributor                              ☑     ☑     ☑
 noi.Customer                           ☑     ☑     ☑     ☑
 noi.Developer                                      ☑     ☑
 noi.SiteAdmin                                            ☑
 office.OfficeStaff                                       ☑
 office.OfficeUser                      ☑     ☑     ☑     ☑
 polls.PollsAdmin                                         ☑
 polls.PollsStaff                             ☑     ☑     ☑
 polls.PollsUser                        ☑     ☑     ☑     ☑
 products.ProductsStaff                                   ☑
 storage.StorageStaff                                     ☑
 storage.StorageUser                                      ☑
 tickets.Reporter                       ☑     ☑     ☑     ☑
 tickets.Searcher                 ☑     ☑     ☑     ☑     ☑
 tickets.TicketsStaff                               ☑     ☑
 tickets.Triager                                    ☑     ☑
 topics.TopicsUser                      ☑     ☑     ☑     ☑
 votes.VotesStaff                                         ☑
 votes.VotesUser                        ☑     ☑     ☑     ☑
 working.Worker                               ☑     ☑     ☑
================================ ===== ===== ===== ===== =====
<BLANKLINE>



The table doesn't show *all* user roles, only those that are "meaningful".

Where meaningful means: those which are mentioned (either imported or defined)
in the global context of the :attr:`user_types_module
<lino.core.site.Site.user_types_module>`. We tried more "intelligent"
approaches, but it is not trivial for Lino to guess which roles are
"meaningful".

Querying users
==============

All users:

>>> users.User.get_active_users()
<QuerySet [User #7 ('Jean'), User #6 ('Luc'), User #4 ('Marc'), User #5 ('Mathieu'), User #3 ('Romain Raffault'), User #2 ('Rolf Rompen'), User #1 ('Robin Rood')]>

Only site administrators:

>>> from lino.core.roles import SiteAdmin
>>> users.User.get_active_users([SiteAdmin])
<QuerySet [User #3 ('Romain Raffault'), User #2 ('Rolf Rompen'), User #1 ('Robin Rood')]>

All except site administrators:

>>> users.User.get_active_users(unwanted_roles=[SiteAdmin])
<QuerySet [User #7 ('Jean'), User #6 ('Luc'), User #4 ('Marc'), User #5 ('Mathieu')]>

All who speak English:

>>> users.User.get_active_users(language="en")
<QuerySet [User #7 ('Jean'), User #6 ('Luc'), User #4 ('Marc'), User #5 ('Mathieu'), User #1 ('Robin Rood')]>




User sessions
=============

.. class:: Sessions

  Show a list of all :term:`user sessions <user session>`.

See :doc:`/dev/sessions`.


Authorities : let other users work in your name
===============================================

.. class:: Authority

    Django model used to represent a :term:`authority`.

    .. attribute:: user

        The user who gives the right of representation. author of this
        authority

    .. attribute:: authorized

        The user who gets the right to represent the author




.. _current_user_type:

The current user type
=====================

This is used by :mod:`lino.utils.jsgen`, i.e. when generating the
:xfile:`linoweb.js` file for a given user type.


Site configuration
====================

This plugin adds the following
:term:`plugin settings <plugin setting>`:

.. setting:: users.third_party_authentication

  Whether this :term:`site <Lino site>` provides third party authentication.

  This should be activated only when there is at least one authentication
  provider.

This plugin has the following :term:`site settings <site setting>`:

.. setting:: users.allow_online_registration

  Whether users can register online. When this is set to `True`, a
  `create_account` action will be available under :class:`About
  <lino.modlib.about.models.About>` actor. This also activates the verification
  system, and on account creation new users are asked to enter a verification
  code to verify their email address.

.. setting:: active_sessions_limit

  The :term:`sessions limit` for this site. The default value `-1` means
  that there is no limitation. Setting this to `0` will prevent any new
  login attempt and might be useful as a temporary value before shutting
  down a site.

.. setting:: users.verification_code_expires = 5

  Number of minutes after which a user :term:`verification code` becomes
  invalid. Used to invalidate a user verification code after the elapsed
  minutes.

.. setting:: users.user_type_new = 'user'

  The default user_type for an unverified user.

.. setting:: users.user_type_verified = 'user'

  The default user_type for a verified user.

.. setting:: users.with_nickname

  Whether to add the :attr:`User.nickname` field.

.. setting:: users.demo_password

  The password to set for users of a :term:`demo site`.

.. data:: demo_username

  The :attr:`username <User.username>` of the *default site user*.

  The username of the root user to use in demo fixtures.

  Default value is ``"robin"`` (except when the Site's first language is not
  English). It is needed on sites that don't have English in their
  :attr:`lino.core.site.Site.languages`.

  The ``checkdata`` fixture uses this.

  This is also the default value for the :meth:`get_responsible_user
  <lino.modlib.checkdata.Checker.get_responsible_user>` method of data checker.


Roles
=====

This plugin defines the following user roles.

.. class:: Helper

    Somebody who can help others by running :class:`AssignToMe`
    action.


.. class:: AuthorshipTaker

    Somebody who can help others by running :class:`TakeAuthorship`
    action.


Actions
=======

.. class:: SendWelcomeMail

    Send a welcome mail to this user.


.. class:: ChangePassword

    Change the password of this user.

    .. attribute:: current

        The current password. Leave empty if the user has no password yet. A
        :term:`site manager` doesn't need to specify this at all.

    .. attribute:: new1

        The new password.

    .. attribute:: new2

        The new password a second time. Both passwords must match.


.. class:: SignIn

    Open a window that asks for username and password and authenticates as this
    user when submitted.

.. class:: SignOut

    Sign out the current user and return to the welcome screen for
    anonymous visitors.

.. class:: CreateAccount

  .. attribute:: first_name

    Your first name.

  .. attribute:: last_name

    Your last name.

  .. attribute:: email

    Your email address. This is required to verify your account.

  .. attribute:: username

    The username you want to get. Leave empty to get your email address as your
    username.

  .. attribute:: password

    Your password.



Model mixins
============

.. class:: Authored

    .. attribute:: manager_roles_required

        The list of required roles for getting permission to edit
        other users' work.

        By default, only :class:`SiteStaff
        <lino.core.roles.SiteStaff>` users can edit other users' work.

        An application can set :attr:`manager_roles_required` to some
        other user role class or a tuple of such classes.

        Setting :attr:`manager_roles_required` to ``[]`` will **disable**
        this behaviour (i.e. everybody can edit the work of other users).

        This is going to be passed to :meth:`has_required_roles
        <lino.core.users.choicelists.UserType.has_required_roles>` of
        the requesting user's profile.

        Usage examples see :class:`lino_xl.lib.notes.models.Note` or
        :class:`lino_xl.lib.cal.Component`.


    .. attribute:: author_field_name

        No longer used. The name of the field that defines the author
        of this object.



.. class:: UserAuthored

    Inherits from :class:`Authored`.

    Mixin for models with a :attr:`user` field that points to
    the "author" of this object. The default user of new instances is
    automatically set to the requesting user.

    .. attribute:: user

        The author of this :term:`database object`.

        A pointer to :class:`lino.modlib.users.models.User`.


.. class:: StartPlan

    The action to start a user plan.

    This is the default implementation for :attr:`UserPlan.start_plan`, but it
    may be subclassed. For example :class:`StartInvoicing
    <lino_xl.lib.invoicing.StartInvoicing>` extends this because there may be
    more than one types of invoicing plans.

    .. attribute:: update_after_start

        Whether to run :meth:`Plan.update_plan` after starting the plan.

.. class:: UserPlan

    Mixin for anything that represents a "plan" of a given user on a given day.

    What a "plan" means, depends on the inheriting child.  Examples are an
    :term:`invoicing plan` (:class:`lino_xl.lib.invoicing.Plan`), a
    :term:`shopping cart` (:class:`lino_xl.lib.shopping.Cart`) or an
    :term:`accounting report` (:class:`lino_xl.lib.sheets.Report`).

    The mixin makes sure that there is only one database instance per user. A
    plan is considered a low value database object to be reused frequently.

    Inherits from :class:`UserAuthored`.

    .. attribute:: user

         The user who owns and uses this plan.

    .. attribute:: today

         This date of this plan.  This is automatically set to today
         each time the plan is called or updated.

    .. attribute:: update_plan_button

    .. method:: create_user_plan(self, user)

        Return the database object for this plan and user.
        or create

    .. method:: update_plan(self, ar)

        Implementing models should provide this method.


.. class:: UpdatePlan

    Build a new list of suggestions.
    This will remove all current suggestions.





doctests
========

Verify whether the help_text of the change_password action is set:

>>> ba = rt.models.users.AllUsers.get_action_by_name('change_password')
>>> print(ba.help_text)
Ask for a new password to be used for authentication.

.. Change the password of this user.

Verify whether :ticket:`3766` is fixed:

>>> show_choices('robin', '/choices/users/Users/partner')
... #doctest: +ELLIPSIS
<BLANKLINE>
AS Express Post
AS Matsalu Veevärk
Altenberg Hans
Arens Andreas
...
Ärgerlich Erna
Õunapuu Õie
Östges Otto

>>> show_choices('robin', '/choices/users/Users/user_type')
<BLANKLINE>
000 (Anonymous)
100 (Customer)
200 (Contributor)
400 (Developer)
900 (Administrator)


Reset password and verify email
===============================

The following actions are available also to anonymous users.


.. currentmodule:: lino.modlib.about

.. class:: About
  :no-index:

    .. attribute:: sign_in

      Ask for your username and password in order to authenticate.

      If :setting:`users.third_party_authentication` is enabled, this also shows
      alternative authentication methods.

    .. attribute:: reset_password

      Ask for your email address and send a verification code.

    .. attribute:: verify_user

      Ask for the verification code you have received by email and mark your
      email address as verified.


User types module
=================

.. currentmodule:: lino.core.site

The default value for :attr:`Site.user_types_module` is `None`, meaning that
permission control is inactive: everything is permitted.   But note that
:meth:`Site.set_user_model` sets it to :mod:`lino.core.user_types`.

This must be set if you want to enable permission control based on
user roles defined in :attr:`Permittable.required_roles
<lino.core.permissions.Permittable.required_roles>` and
:attr:`UserType.role
<lino.modlib.users.UserType.role>`.

If set, Lino will import the named module during site startup. It is expected to
define application-specific user roles (if necessary) and to populate the
:class:`UserTypes` choicelist.

Examples of such user types modules are
:mod:`lino.core.user_types` and
:mod:`lino_noi.lib.noi.user_types`.


The welcome message
===================

.. xfile:: users/welcome_email.eml

  The template used to generate the welcome email to new users.

Here are several ways for generating the verify link in the
:xfile:`users/welcome_email.eml`.

A first series used the instance action:

>>> ar = rt.login("robin", renderer=settings.SITE.kernel.default_renderer)
>>> obj = ar.get_user()
>>> ar.permalink_uris = True
>>> print(tostring(ar.instance_action_button(
...  obj.verify_me, request_kwargs=dict(action_param_values=dict(
...    email="foo@example.com", verification_code="123")))))  #doctest: +ELLIPSIS
<a href="/api/users/AllUsers/1?fv=123&amp;an=verify_me" title="Ask ... verified." style="text-decoration:none">Verify</a>
>>> # ba = users.Users.get_action_by_name('verify')
>>> url = ar.get_permalink(obj.verify_me.bound_action, obj, email="foo@example.com", verification_code="123")
>>> print(url)
/api/users/AllUsers/1?fv=123&an=verify_me

But this wasn't good because it uses the :class:`lino.modlib.users.AllUsers`
:term:`data table`, which is visible only to :class:`SiteAdmin`.

>>> ba = users.Me.get_action_by_name('verify_me')
>>> pv = dict(email="foo@example.com", verification_code="123")
>>> from lino.api import _
>>> print(tostring(ar.row_action_button(
...    obj, ba, _("Click here to verify"),
...    request_kwargs=dict(action_param_values=pv))))  #doctest: +ELLIPSIS
<a href="/api/users/Me/1?fv=123&amp;an=verify_me" title="Ask ... mark your email address as verified." style="text-decoration:none">Click here to verify</a>

But even this had the disadvantage that the user had to sign in before being
able to verify.

>>> ba = about.About.get_action_by_name('verify_user')
>>> pv = dict(email="foo@example.com", verification_code="123")
>>> from lino.api import _
>>> print(tostring(ar.row_action_button(
...    obj, ba, _("Click here to verify"),
...    request_kwargs=dict(action_param_values=pv))))
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
<a href="/api/about/About?fv=foo%40example.com&amp;fv=123&amp;an=verify_user"
  title="Ask ... verified." style="text-decoration:none">Click here to verify</a>


Note how :class:`lino.modlib.users.User.verify_me` inherits from
:attr:`lino.modlib.about.About.verify_user`. They do the same, but in different
contexts.

TODO: Is there a more intuitive syntax for rendering our button?

Here is a first attempt, which works only for row actions:

>>> sar = obj.verify_me.request_from(ar, action_param_values=dict(
...    email="foo@example.com", verification_code="123"), permalink_uris=True)
>>> sar.permalink_uris = True
>>> print(tostring(sar.row_action_button_ar(obj)))
... #doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
<a href="javascript:window.App.runAction(...)" title="..."
  style="text-decoration:none">Verify</a>

Here is a second attempt (used since 20240407):

>>> print(ar.action_link("about.About.verify_user",
...     text=_("click here to verify"),
...     pv=dict(email=obj.email, verification_code="123")))
... #doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
<a href="/api/about/About?fv=demo%40example.com&amp;fv=123&amp;an=verify_user"
style="text-decoration:none">click here to verify</a>


In the body of the :file:`welcome_message.eml`, we use
:attr:`lino.core.site.Site.server_url` as a ``base href`` header field::

  <html><head><base href="{{settings.SITE.server_url}}" target="_blank"></head><body>

>>> print(settings.SITE.server_url)
http://127.0.0.1:8000




Utility functions
=================


.. function:: with_user_profile(profile, func, *args, **kwargs)

  Run the given callable `func` with the given user type
  activated. Optional args and kwargs are forwarded to the callable,
  and the return value is returned.

  This might get deprecated some day since we now have the
  :meth:`UserType.context` method
