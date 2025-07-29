..  doctest docs/dev/polls/index.rst
.. _lino.tutorial.polls:

=======================
The Lino Polls tutorial
=======================

.. doctest init:
    >>> import lino,os,sys
    >>> os.chdir('lino_book/projects/polls')
    >>> sys.path.append('.')
    >>> lino.startup('lino_book.projects.polls.mysite.settings')
    >>> from lino.api.doctest import *

Congratulations, you have reached the last tutorial of the "Get started"
section!

In this tutorial we are going to convert the "Polls" application of Django's
famous `Writing your first Django app
<https://docs.djangoproject.com/en/5.0/intro/>`__ tutorial into a Lino
application. This will illustrate some :doc:`differences between Lino and Django
</dev/about/lino_and_django>`. A lot of Django know-how applies to Lino as well,
but there are also some fundamental differences.

In the early days of the Lino Developer Guide, this tutorial was the first thing
we asked new developers to do. That's why you will hopefully have a *déjà-vu*
feeling at certain places. But don't be afraid of repeating things: every single
action of this tutorial is a useful exercise for a software developer.


.. currentmodule:: lino.core.site

.. contents:: Table of Contents
 :local:
 :depth: 2


Two parts of the Django tutorial
--------------------------------

For this tutorial we ask you to follow **parts 1 and 2** of the **Django
tutorial**. But before diving into these documents a couple of remarks about how
to read them:

- Don't worry if you find the `Write your first view
  <https://docs.djangoproject.com/en/5.0/intro/tutorial01/#write-your-first-view>`__
  section in part 1 difficult, in Lino you don't need to write views.

- The `Explore the free admin functionality
  <https://docs.djangoproject.com/en/5.0/intro/tutorial02/#explore-the-free-admin-functionality>`__
  section in part 2 shows what you are going to *not* need with Lino because
  Lino is an alternative to Django's Admin interface.

- Of course you may follow the whole `Getting started
  <https://docs.djangoproject.com/en/5.0/intro/>`_ section of the Django
  tutorial, but with Lino you won't need many things explained there.

Seat belts fastened? Here we go! Please follow **parts 1 and 2** of the **Django
tutorial** now:

- `Writing your first Django app, part 1
  <https://docs.djangoproject.com/en/5.0/intro/tutorial01/>`__.
- `Writing your first Django app, part 2
  <https://docs.djangoproject.com/en/5.0/intro/tutorial02/>`__.

Welcome back. I hope you enjoyed the trip.  Summary of what you should have done
on your machine::

    $ cd ~/projects
    $ django-admin startproject mysite
    $ cd mysite
    $ python manage.py startapp polls
    $ nano polls/views.py
    $ nano polls/urls.py
    $ nano mysite/urls.py
    $ nano mysite/settings.py
    $ nano polls/models.py
    $ python manage.py migrate

We now leave the Django world and continue "the Lino way" of writing web
applications.

From Django to Lino
-------------------

You should now have a set of files in your "project directory"::

    mysite/
        manage.py
        mysite/
            __init__.py
            settings.py
            urls.py
            wsgi.py
        polls/
            __init__.py
            admin.py
            apps.py
            migrations/
                __init__.py
            models.py
            tests.py
            urls.py
            views.py

Some of these files remain unchanged: :xfile:`__init__.py`,
:xfile:`manage.py` and :xfile:`wsgi.py`.

Now **delete** the following files (feel free to make a backup first)::

  $ rm mysite/urls.py
  $ rm polls/urls.py
  $ rm polls/views.py
  $ rm polls/admin.py
  $ rm polls/apps.py
  $ rm -R polls/migrations

It is especially important to delete the :file:`migrations` directory and its
content because they would interfere with what we are going to show you in this
tutorial. The other files will just become useless.

And in the following sections we are going to **modify** the files
:file:`mysite/settings.py` and :file:`polls/models.py`.

.. _dev.polls.settings:

The :file:`mysite/settings.py` file
-----------------------------------

Please change the contents of your :xfile:`settings.py` to the
following:

.. literalinclude:: /../../book/lino_book/projects/polls/mysite/settings.py

A few explanations:

#.  A Lino :xfile:`settings.py` file always defines (or imports) a
    **class** named ``Site`` which is a direct or indirect descendant of
    :class:`lino.core.site.Site`.  Our example also **overrides** that
    class before instantiating it.

#.  We are using the rather uncommon construct of overriding a class
    by a class of the same name. This might look surprising. You might
    prefer to give a new name::

      class MySite(Site):
          ...
          ... super(MySite, self)....

      SITE = MySite()

    It's a matter of taste. But overriding a class by a class of the
    same name is perfectly allowed in Python, and you must know that
    as a Lino developer your are going to write *many* subclasses of
    :class:`Site` and subclasses thereof. I got tired of always
    finding new class names like MySite, MyNewSite, MyBetter
    VariantOfNewSite...

#.  In the line ``SITE = Site(globals())`` we **instantiate** our
    class into a variable named ``SITE``. Note that we pass our
    :func:`globals` `dict` to Lino. Lino needs this to insert all
    those Django settings into the global namespace of our settings
    module.

#.  One of the Django settings managed by Lino is
    :setting:`INSTALLED_APPS`. In Lino you don't code this setting
    directly into your :xfile:`settings.py` file, you override your
    Site's :meth:`get_installed_plugins
    <lino.core.site.Site.get_installed_plugins>` method.  Our example
    does the equivalent of ``INSTALLED_APPS = ['polls']``, except for
    the fact that Lino automagically adds some more apps.

#.  The **main menu** of a Lino application is defined in the
    :meth:`setup_menu <lino.core.site.Site.setup_menu>` method.  At
    least in the simplest case.  More about this in :doc:`/dev/menu`.

Lino uses some tricks to make Django settings modules more pleasant to work
with, especially if you maintain Lino sites for several customers. We will come
back to this in :doc:`/dev/site`

..
    >>> pprint(settings.INSTALLED_APPS)
    ('lino',
     'lino.modlib.about',
     'lino.modlib.jinja',
     'lino_react.react',
     'lino_book.projects.polls.polls',
     'django.contrib.staticfiles')


The :file:`polls/models.py` file
--------------------------------

Please change the contents of your :file:`polls/models.py` to the
following:

.. literalinclude:: /../../book/lino_book/projects/polls/polls/models.py

A few explanations while looking at that file:

- The :mod:`lino.api.dd` module is a shortcut to most Lino extensions
  used by :term:`application developers <application developer>` in their :xfile:`models.py` modules.
  ``dd`` stands for "data definition".

- :class:`dd.Model <lino.core.model.Model>` is an optional (but
  recommended) wrapper around Django's Model class.  For this tutorial
  you could use Django's `models.Model` as well, but in general we
  recommend to use :class:`dd.Model <lino.core.model.Model>`.

- There's one **custom action** in our application, defined as the
  `vote` method on the :class:`Choice` model, using the
  :func:`dd.action <lino.core.actions.action>` decorator. More about
  actions in :ref:`dev.actions`.


The :file:`polls/ui.py` file
---------------------------------

Now please create a file named :file:`ui.py` in the same directory as your
:xfile:`models.py`, with the following content.

.. literalinclude:: /../../book/lino_book/projects/polls/polls/ui.py

This file defines three **tables** for our application.  Tables are a new
concept in Lino.  We will learn more about them in another tutorial
:ref:`lino.tutorial.tables`.  For now just note that

- we defined one table per model (`Questions` for the `Question` model
  and `Choices` for the `Choice` model)

- we defined one additional table `ChoicesByQuestion` which inherits
  from `Choices`. This table shows the choices *for a given question*.
  We call it a :ref:`slave table <slave_tables>` because it *depends*
  on its "master" (the given question instance).


Changing the database structure
-------------------------------

One more thing before seeing a result.  We made a little change in our
database schema after the Django tutorial: in our :xfile:`models.py`
file we added the `hidden` field of a Question ::

    hidden = models.BooleanField(
        "Hidden",
        help_text="Whether this poll should not be shown in the main window.",
        default=False)

You have learned what this means: Django (and Lino) "know" that we
added a field named `hidden` in the `Questions` table of our database,
but the *database* doesn't yet know it.  If you would run your
application now, then you would get some error message about unapplied
migrations or some "operational" database error because Lino would ask
the database to read or update this field, and the database would
answer that there is no field named "hidden".  We must tell our
database that the structure has changed.

For the moment we are just going to *reinitialize* our database,
i.e. *delete* any data you may have manually entered during the Django
Polls tutorial and turn the database into a virgin state::

    $ python manage.py initdb

The output should be::

    We are going to flush your database (/home/luc/projects/mysite/mysite/default.db).
    Are you sure (y/n) ? [Y,n]?
    `initdb ` started on database /home/luc/projects/mysite/mysite/default.db.
    Operations to perform:
      Synchronize unmigrated apps: about, jinja, staticfiles, lino, extjs, bootstrap3
      Apply all migrations: polls
    Synchronizing apps without migrations:
      Creating tables...
        Running deferred SQL...
    Running migrations:
      Rendering model states... DONE
      Applying polls.0001_initial... OK


..
    >>> from django.core.management import call_command
    >>> call_command('initdb', interactive=False, verbosity=0)


Adding a demo fixture
---------------------

Now we hope that you are a bit frustrated about seeing gone forever all that
beautiful data you manually entered during the Django Polls tutorial. This is
the moment for introducing you to :term:`demo fixtures`.

When you develop and maintain a database application, it happens often
that you need to change the database structure.  Instead of manually
filling your demo data again and again after every database change, we
prefer writing it *once and for all* as a *fixture*.  With Lino this
is easy and fun because you can write fixtures in Python.

- Create a directory named :file:`fixtures` in your :file:`polls`
  directory.

- Create an empty file named :xfile:`__init__.py` in that directory.

- Still in the same directory, create another file named ``demo.py``
  with the following content:

.. literalinclude:: /../../book/lino_book/projects/polls/polls/fixtures/demo1.py

- If you prefer, the following code does exactly the same but has the
  advantage of being more easy to maintain:

.. literalinclude:: /../../book/lino_book/projects/polls/polls/fixtures/demo.py

- Run the following command (from your project directory)
  to install these fixtures::

    $ python manage.py initdb demo

  This means "Initialize my database and apply all fixtures named
  :file:`demo`".  The output should be::

    Operations to perform:
      Synchronize unmigrated apps: about, jinja, staticfiles, polls, lino, extjs, bootstrap3
      Apply all migrations: (none)
    Synchronizing apps without migrations:
      Creating tables...
        Running deferred SQL...
    Running migrations:
      No migrations to apply.
    Loading data from ...
    Installed 13 object(s) from 1 fixture(s)

.. the following is tested, but not rendered to HTML:

    >>> call_command('initdb', 'demo', interactive=False, verbosity=0)
    ... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    Loading data from .../projects/polls/polls/fixtures/demo.py
    >>> rt.show('polls.Questions')  #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    ==== ================================ ===================== ========
     ID   Question text                    Date published        Hidden
    ---- -------------------------------- --------------------- --------
     1    What is your preferred colour?   ...        00:00:00   No
     2    Do you like Django?              ...        00:00:00   No
     3    Do you like ExtJS?               ...        00:00:00   No
    ==== ================================ ===================== ========
    <BLANKLINE>

    >>> call_command('initdb', 'demo1', interactive=False, verbosity=0)
    ... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    Loading data from .../projects/polls/polls/fixtures/demo1.py
    >>> rt.show('polls.Questions')  #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    ==== ================================ ===================== ========
     ID   Question text                    Date published        Hidden
    ---- -------------------------------- --------------------- --------
     1    What is your preferred colour?   ...        00:00:00   No
     2    Do you like Django?              ...        00:00:00   No
     3    Do you like ExtJS?               ...        00:00:00   No
    ==== ================================ ===================== ========
    <BLANKLINE>


    >>> # test_client.get("123")
    >>> walk_menu_items()
    - Polls --> Questions : 4
    - Polls --> Choices : 11
    - Site --> About : (not tested)
    <BLANKLINE>

    TODO: above snippet should show 5 questions (4+1 for the phantom
    row) and 11 choices. It seems that everything is duplicated
    because `initdb` does nothing when database is `:memory:`.

You might now want to read more about :doc:`Python fixtures
</dev/pyfixtures/index>` or Lino's special approach for :doc:`migrating
data </dev/datamig>`...  or simply stay with us and learn by doing!


Starting the web interface
--------------------------

Now we are ready to start the development web server on our project::

  $ cd ~/mypy/mysite
  $ python manage.py runserver

and point your browser to http://127.0.0.1:8000/ to see your first
Lino application running. It should look something like this:q

.. image:: main1.png
    :scale: 50

Please play around and check whether everything works as expected
before reading on.



The main index
--------------

Now let's customize our **main window** (or *index view*, or :term:`dashboard`).
Lino uses a template named :xfile:`admin_main.html` for rendering the HTML to be
displayed there.  We are going to **override** that template.

Please create a directory named :file:`mysite/config`, and in that
directory create a file named :xfile:`admin_main.html` with the
following content:

.. literalinclude:: /../../book/lino_book/projects/polls/mysite/config/admin_main.html

Explanations:

- :attr:`rt.models <lino.core.site.Site.models>` : is a shortcut to
  access the models and tables of the application.  In plain Django
  you learned to write::

    from polls.models import Question

  But in Lino we recommend to write::

    Question = rt.models.polls.Question

  because the former hard-wires the location of the `polls` plugin.
  If you do it the plain Django way, you are going to miss
  :doc:`plugin inheritence </dev/plugin_inheritance>`.

- If `objects`, `filter()` and `order_by()` are new to you, then
  please read the `Making queries
  <https://docs.djangoproject.com/en/5.0/topics/db/queries>`__ chapter
  of Django's documentation.  Lino is based on Django, and Django is
  known for its good documentation. Use it!

- If `joiner` and `sep` are a riddle to you, you'll find the solution
  in Jinja's `Template Designer Documentation
  <http://jinja.pocoo.org/docs/templates/#joiner>`__.  Lino
  applications replace Django's template engine by `Jinja
  <http://jinja.pocoo.org>`__.

- ``obj.vote`` is an :class:`InstanceAction
  <lino.core.actions.InstanceAction>` object, and we call its
  :meth:`as_button <lino.core.actions.InstanceAction.as_button>`
  method which returns a HTML fragment that displays a button-like
  link which will run the action when clicked.  More about this in
  :ref:`dev.actions`.

- The :func:`fdl` function is a Lino-specific template function. These are
  currently not well documented, you must consult the code that edefines them,
  e.g. the :meth:`get_printable_context
  <lino.core.requests.BaseRequest.get_printable_context>` method.


As a result, our main window now features a summary of the currently
opened polls:

.. image:: main2.png
    :scale: 50

Note that writing your own :xfile:`admin_main.html` template is the
easiest but also the most primitive way of bringing content to the
main window.  In real world applications you will probably use
dashboard items as described in :doc:`/dev/admin_main`.

After clicking on a vote, here is the `vote` method
of our `Choice` model in action:

.. image:: polls2.jpg
    :scale: 50


After selecting :menuselection:`Polls --> Questions` in the main menu,
Lino opens that table in a **grid window**:

.. image:: polls3.jpg
    :scale: 50

Every table can be displayed in a **grid window**, a tabular
representation with common functionality such as sorting,
setting column filters, editing individual cells,
and a context menu.

After double-clicking on a row in the previous screen, Lino shows the
**detail window** on that Question:

.. image:: polls4.jpg
    :scale: 50

This window has been designed by the following code in your
:file:`desktop.py` file::

    detail_layout = """
    id question_text
    hidden pub_date
    ChoicesByQuestion
    """

Yes, nothing else. To add a detail window to a table, you simply add a
:attr:`detail_layout <lino.core.actors.Actor.detail_layout>` attribute
to the Table's class definition.

  **Exercise**: comment out above lines in your code and observe how
  the application's behaviour changes.

Not all tables have a detail window.  In our case the `Questions`
table has one, but the `Choices` and `ChoicesByQuestion` tables don't.
Double-clicking on a cell of a Question will open the Detail Window,
but double-clicking on a cell of a Choice will start cell editing.
Note that you can still edit an individual cell of a Question in a
grid window by pressing the :kbd:`F2` key.


After clicking the :guilabel:`New` button, you can admire an **Insert
Window**:

.. image:: polls5.jpg
    :scale: 50

This window layout is defined by the following :attr:`insert_layout
<lino.core.actors.Actor.insert_layout>` attribute::

    insert_layout = """
    question
    hidden
    """

See :doc:`/tutorials/layouts` for more explanations.

After clicking the :guilabel:`[html]` button:

.. image:: polls6.jpg
    :scale: 50


Exercises
---------

#.  **Add the current score** of each choice to the results in your
    customized :xfile:`admin_main.html` file.

#.  **Adding more explanations**

    Imagine that your customer asks you to add a possibility for
    specifying a longer explanation text for every question. The
    question's title should show up in bold, and the longer
    explanation should come before the "Published..." part

    Hint: add a `TextField` named `question_help` to your `Question`
    model, add this field to the `detail_layout` of your `Questions`
    table, modify your `admin_main.html` file so that the field content is
    displayed, optionally modify your :file:`demo.py` fixture, finally run
    :cmd:`pm prep` again before launching :manage:`runserver`.

See solutions to these in :mod:`lino_book.projects.polls2`

Summary
-------

In this tutorial we followed the first two chapters of the Django
Tutorial, then converted their result into a Lino application.  We
learned more about python fixtures, tables, actions, layouts and
menus.
