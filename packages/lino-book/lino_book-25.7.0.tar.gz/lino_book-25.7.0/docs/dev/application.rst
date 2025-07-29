.. _application:

=======================
What is an application?
=======================

.. currentmodule:: lino.core.site

One of the important things to understand when you learn Lino is the
:class:`Site` class. A :class:`Site` represents an *application*.

An application, for Lino, is a *standalone piece of software* that is
*perceived as an entity* by *end-users*.

    An **application program** (app or application for short) is a
    computer program designed to perform a group of coordinated
    functions, tasks, or activities for the benefit of the user.  --
    `Wikipedia <https://en.wikipedia.org/wiki/Application_software>`_

Django comes with a rather special use of the word 'application'.
Daniel and Audrey (`Two scoops of Django
<http://twoscoopspress.org/products/two-scoops-of-django-1-6>`_) say
it in a diplomatic way: "It's not uncommon for new Django developers
to become understandably confused by Django's usage of the word
'app'."  But to be honest: Django is *simply wrong* at this point.  It
says "application" where it should say "plugin" or "module". Things
like `django.contrib.contenttypes
<https://docs.djangoproject.com/en/5.0/ref/contrib/contenttypes/>`_
are not what normal people would call an "application", they are
rather "plugins" or "modules".

That said, we will of course forgive Django this oddness, which has
understandable historical reasons.  After all it is basically just a
vocabulary problem.  Many Django people are more or less aware of that
problem, but it would be really much work to fix it because the word
is used in variables like `app_label` and :setting:`INSTALLED_APPS`.
Too much work for "just a vocabulary" problem.

.. As a compromise, we suggest to just change the documentation.  We
   suggest to differentiate between "app" and "application".  We can
   continue to call them "apps", but should refrain from expanding
   that word to "application".  Because apps are *not* applications,
   they are plugins which we happen to call "app" for historical
   reasons.  This rule shouldn't offend even the most conservative
   Django developer.  Unfortunately, the Django developers did not
   know about these considerations when the worked on version
   1.7. That's why they continue to speak about `Applications
   <https://docs.djangoproject.com/en/5.0/ref/applications/>`_,
   ignoring our vocabulary problem.

The "only" problem with this vocabulary problem is that it leaves us
(Lino developers) with no word left for what **we** would want to call
an application.  A Lino application is neither an "app" nor a
"project".

That's why we chose :class:`Site` as the name for the class which
describes an *application* (as Lino understands it), and the
:class:`Plugin <lino.core.plugin.Plugin>` class as a wrapper for what
Django calls "applications".

Lino's :class:`Plugin <lino.core.plugin.Plugin>` class is comparable to Django's
`AppConfig <https://docs.djangoproject.com/en/5.0/ref/applications/>`_ class,
but has some additional features, which makes them the preferred way.
