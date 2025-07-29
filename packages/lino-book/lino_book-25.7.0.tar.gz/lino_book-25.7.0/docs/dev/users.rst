.. doctest docs/dev/users.rst
.. _dev.users:

===============================
Introduction to user management
===============================

This page explains to developers and server administrators how to get
started with Lino's functionality for managing the users of a :term:`Lino site`.

It assumes that you have read the end-user documentation about
:ref:`ug.plugins.users`.

See :doc:`/plugins/users` for detailed developer documentation.

.. contents::
    :depth: 1
    :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino import startup
>>> startup('lino_book.projects.min1.settings')
>>> from lino.api.doctest import *
>>> from atelier.sheller import Sheller
>>> shell = Sheller("lino_book/projects/min1")

Creating a site manager
=======================

A :term:`site manager` is any :term:`site user`  having "Administrator" as
:term:`user type`, which gives them permission to **edit the list of site
users**.

On a default Lino site this permission is given only to the "Administrator"
:term:`user type`. More precisely this permission is given by the
:class:`SiteAdmin <lino.core.roles.SiteAdmin>` :term:`user role`, which is
inherited by the "Administrator" :term:`user type`,  and  an application can use
a custom `user_types_module
<https://dev.lino-framework.org/plugins/users.html#user-types-module>`__ to
define other user types.

The most Linoish way to create a :term:`site manager` and a set of demo
users is to run :cmd:`pm prep`.  This will reset the database to a virgin state
and then load the :fixture:`demo` fixture, which will create the demo users
Robin, Rolf, Romain, Rando, Rik, Ronaldo ... depending on your site's
:term:`language distribution` (:attr:`lino.core.site.Site.languages`).

Once you have a site manager, you can sign in via the web interface and
work as described in :ref:`ug.plugins.users`.


Managing users from the command line
====================================

Django has a :term:`django-admin command` named :manage:`createsuperuser`  but
this is quite limited. Lino gives a more useful command :manage:`passwd`.

.. management_command:: passwd

.. program:: passwd

Update or optionally create password, name and type of a user. The default
action displays and optionally edits the user. Specify :option:`-c` to create a
new user.

Usage: go to your project directory and say::

  $ python manage.py passwd [options] USERNAME

Where USERNAME is the username of the user to process.
Default value for ``USERNAME`` is your system username.


.. rubric:: Options


.. option:: -c, --create

  Create the given user. Fail if that username exists already.

.. option:: --batch

    Run in batch mode, i.e. without asking any questions.
    Assume yes to all questions.

.. # tidy up
  >>> try:
  ...     users.User.objects.get(username="test").delete()
  ... except users.User.DoesNotExist:
  ...    pass


>>> shell("python manage.py show users.AllUsers")
... #doctest: +ELLIPSIS
========== ===================== ============ ===========
 Username   User type             First name   Last name
---------- --------------------- ------------ -----------
 robin      900 (Administrator)   Robin        Rood
 rolf       900 (Administrator)   Rolf         Rompen
 romain     900 (Administrator)   Romain       Raffault
========== ===================== ============ ===========

>>> shell("python manage.py passwd -c test --batch")
Creating new user
User test has been saved.

>>> shell("python manage.py show users.AllUsers")
... #doctest: +ELLIPSIS
========== ===================== ============ ===========
 Username   User type             First name   Last name
---------- --------------------- ------------ -----------
 robin      900 (Administrator)   Robin        Rood
 rolf       900 (Administrator)   Rolf         Rompen
 romain     900 (Administrator)   Romain       Raffault
 test
========== ===================== ============ ===========

>>> u = users.User.objects.get(username="test")
>>> u.has_usable_password()
False



Managing users programmatically
====================================

For more fancy situations you can write a Python script and run it with
:cmd:`pm run`. For example::

    from lino.api.shell import users
    obj = users.User(username="root")
    obj.set_password("1234!")
    obj.full_clean()
    obj.save()



Passwords of new users
======================

The `password` field of a newly created user is empty, and the account therefore
cannot be used to sign in.  When you created a new user manually using the web
interface, you must click their :class:`ChangePassword` action and set their
password.

.. # tidy up
  >>> try:
  ...     users.User.objects.get(username="test").delete()
  ... except users.User.DoesNotExist:
  ...    pass

>>> u = users.User(username="test")
>>> u.full_clean()
>>> u.save()

Since we didn't set a `password`, Django stores a "non usable" password, and the
:meth:`User.check_password` method returns `False`:

>>> u.password  #doctest: +ELLIPSIS
'!...'
>>> u.check_password('')
False

>>> u.has_usable_password()
False


When setting the password for a newly created user, leave the
field :guilabel:`Current password` empty.

>>> ses = rt.login('robin')
>>> values = dict(current="", new1="2rgXx2EdJp", new2="2rgXx2EdJp")
>>> rv = ses.run(u.change_password, action_param_values=values)
>>> print(rv['message'])
New password has been set for test.

>>> u.delete()

.. _dev.users.password_validation:

Password validation
===================

A Lino site defaults to use the four password validators that come `included
with Django
<https://docs.djangoproject.com/en/5.1/topics/auth/passwords/#included-validators>`__:

>>> pprint(settings.AUTH_PASSWORD_VALIDATORS)
[{'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
 {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
 {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
 {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'}]

See also the Django docs about `Password validation
<https://docs.djangoproject.com/en/5.1/topics/auth/passwords/#module-django.contrib.auth.password_validation>`__

Note that password validators are being run only in situations where a
potentially naive :term:`end user` is being asked to provide a password. They do
not apply e.g. when a user is created programmatically or when the password is
set at the command line using :cmd:`pm passwd`.

That's why the :term:`demo fixtures` of the :mod:`lino.modlib.users` plugin can
create users with such a terrible password as "1234".

A :term:`server administrator` can customize password validation by manually
setting a custom :setting:`AUTH_PASSWORD_VALIDATORS`.  To disable password
validation alltogether, just add the following line at the end of your
:xfile:`settings.py` file::

  AUTH_PASSWORD_VALIDATORS = []
