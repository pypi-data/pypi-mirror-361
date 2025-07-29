.. doctest docs/dev/hello/index.rst
.. _lino.tutorial.hello:

=================================
Create your first Lino site
=================================

.. contents::
    :depth: 1
    :local:

Create your first Lino site
===========================

Run :cmd:`getlino startsite` to create a first site::

  $ getlino startsite polly first

The first argument ("polly") is the nickname of the application to install.
Run :cmd:`getlino list` to get a list of available choices.

The second argument ("first") is the nickname you give to your Lino site.

Run :manage:`runserver`::

  $ go first
  $ runserver

Start your browser and point it to http://127.0.0.1:8000/

You should see something like the image in :doc:`/dev/install/index`.

It looks the same because it is the same **application** (Polly), but the files
are organized differently. This is no longer a :term:`demo project`, it is the
first :term:`Lino site` running on your machine.


File locations
==============

.. xfile::  ~/lino/lino_local

This is your **projects root**, the base directory for every project of which
*you* are the author. Every new Lino site created with :cmd:`getlino startsite`
will be a directory below this one.

.. xfile::  ~/lino/lino_local/first

This directory contains the first site you just created.
It is a :term:`Django project directory`.

.. glossary::

  Django project directory

    A directory that contains a runnable Django project. It contains the files
    necessary for that specific instance of a given :term:`Lino application`.

Usually there is one :term:`Django project directory` for every :term:`Lino
site`.

..
  (An exception to that rule is a :ref:`site with multiple front ends
  <hosting.multiple_frontends>`, you may leave this for later).

Lino project directories are not very big, and you will hopefully create many
such projects and want to keep a backup of them.

Let's have a look at the files in :xfile:`~/lino/lino_local/first`.

The ``settings.py`` file
========================

Your first :xfile:`settings.py` file should look as follows:

.. literalinclude:: settings.py

Explanations:

- It imports the settings from :mod:`lino_noi.lib.noi.settings` because you said
  ``noi`` as the application for our first site. It imports them directly into
  your global namespace using the wildcard ``*``. Yes, you want them to become
  our Django settings.

- It then does the same with the :mod:`lino_local.settings`. This module has
  been created by :cmd:`getlino configure`, its source code is in
  :file:`~/lino/lino_local/settings.py`, and it contains Django settings
  that are likely to be the same for all Lino sites on a same server. For
  example :setting:`ADMINS`, :setting:`EMAIL_HOST` or :setting:`SERVER_EMAIL`

- Then you redefine the :class:`Site` class using local settings.

- Then comes the trick that turns your Django project into a Lino application::

     SITE = Site(globals(), ...)

  That is, you *instantiate* a :class:`Site <lino.core.site.Site>` class and
  store this object as :setting:`SITE` in your Django settings. This line will
  automatically install default values for all required Django settings (e.g.
  :setting:`DATABASES` and :setting:`LOGGING`) into your global namespace.

You might add ``DEBUG = True`` or other settings of your choice
*after* these two lines.

More about the :xfile:`settings.py` file in :ref:`howto.settings`.


The ``manage.py`` file
=======================

The :xfile:`manage.py` file should have the following content:

.. literalinclude:: manage.py

A :xfile:`manage.py` file does two things: it sets the
:envvar:`DJANGO_SETTINGS_MODULE` environment variable and then calls Django's
:func:`execute_from_command_line
<django.core.management.execute_from_command_line>` function.

..
  Actually a :term:`Lino site` calls
  :func:`lino.core.management.execute_from_command_line`, a wrapper around
  Django's original. It adds functionality for automatically running asynchronously when :setting:`use_linod`




.. this is already in /dev/install/index.rst

  Start the web server

  Now you can invoke :manage:`runserver` to start the development
  server::

    $ python manage.py runserver

  which should output something like::

    Validating models...
    0 errors found
    Django version 1.4.5, using settings 'hello.settings'
    Development server is running at http://127.0.0.1:8000/
    Quit the server with CTRL-BREAK.

  And then point your web browser to http://127.0.0.1:8000 and you
  should see something like this:

  .. image:: hello1.png

  Congratulations! Enjoy the first Lino application that exists only on
  your machine!


Visualizing database content from the command-line
==================================================

The :manage:`runserver` command starts a web server and lets you
interact with the database through the web interface. But Django also
offers a :manage:`shell` interface.
We will come back to this later, for the moment just try the following.

You can visualize the content of your database from the command-line
without starting a web server using Lino's :manage:`show` command.
For example to see the list of countries, you can write::

  $ python manage.py show polls.Polls

This will produce the following output::

  =========== ============================== ============ ========
   Reference   Heading                        Author       State
  ----------- ------------------------------ ------------ --------
               Customer Satisfaction Survey   Robin Rood   Active
               Participant feedback           Robin Rood   Active
               Political compass              Robin Rood   Active
  =========== ============================== ============ ========


Exercises
=========

You can now play around by changing things in your project.

#.  In your :file:`settings.py` file, replace
    :mod:`lino_book.projects.polly.settings` by :mod:`lino_noi.lib.noi.settings`.
    Run :cmd:`pm prep` followed by :cmd:`pm runserver`. Log in and play around.

#.  Same as previous, but with :mod:`lino_book.projects.chatter`

#.  Technically speaking, Polly, Noi and Chatter are different
    :term:`Lino applications
    <Lino application>`. What does Polly do? And what does Chatter do?

#.  Find the source code of the
    :mod:`lino_noi.lib.noi.settings` file.
    Say :cmd:`pywhich lino_noi` to get a hint where this source code is stored.

#.  Read the documentation about the following Site attributes and
    try to change them:

    - :attr:`is_demo_site <lino.core.site.Site.is_demo_site>`
    - :setting:`languages`
    - :setting:`default_ui`

..
  #.  Write three descriptions (e.g. in LibreOffice `.odt` format), one for
      each of the applications you just saw: what it can do, what are
      the features, what functionalities are missing. Use screenshots.
      Use a language that can be understood by non-programmers.  Send
      these documents to your mentor.



Checkpoint
==========

If you follow an internship, you should now have a meeting with your mentor and
show him what you learned so far. You'll get a badge to certify your progress.
