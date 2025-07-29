=============================
About `django-admin` commands
=============================

Lino applications are Django projects. Here is some more Django
know-how you should know as a Lino developer.

The :xfile:`manage.py` file in every demo project is the standard Django
interface for running a so-called :term:`django-admin command`.

.. glossary::

  django-admin command

    A command-line tool to be used for executing diverse tasks on a :term:`Lino
    site`.  On a Lino site we usually say use the :cmd:`pm` alias.

See also the Django docs about `django-admin and manage.py
<https://docs.djangoproject.com/en/5.0/ref/django-admin/>`__ and `Writing
custom django-admin commands
<https://docs.djangoproject.com/en/5.0/howto/custom-management-commands/>`_

Here are some standard :term:`django-admin commands <django-admin command>`  you
should know.

.. management_command:: shell

  Start an interactive Python session on this :term:`site <Lino site>`.

  See the `Django documentation
  <https://docs.djangoproject.com/en/5.0/ref/django-admin/#shell>`__

.. management_command:: runserver

  Start a web server that runs the :term:`application <Lino application>`
  defined by this :term:`site <Lino site>`.

  See the `Django documentation
  <https://docs.djangoproject.com/en/5.0/ref/django-admin/#runserver>`__


.. management_command:: dumpdata

    Output all data in the database (or some tables) to a serialized
    stream.  Serialization formats include *json* or *xml*.  The
    default will write to `stdout`, but you usually redirect this into
    a file.  See the `Django documentation
    <https://docs.djangoproject.com/en/5.0/ref/django-admin/#dumpdata>`__

    With a :term:`Lino application` you will probably prefer :cmd:`pm dump2py`.

.. management_command:: flush

    Removes all data from the database and re-executes any
    post-synchronization handlers. The migrations history is not
    cleared.  If you would rather start from an empty database and
    re-run all migrations, you should drop and recreate the database
    and then run :manage:`migrate` instead.  See the `Django
    documentation
    <https://docs.djangoproject.com/en/5.0/ref/django-admin/#flush>`__

    With a :term:`Lino application` you will probably prefer :manage:`initdb` or
    :cmd:`pm prep`.


.. management_command:: loaddata

    Loads the contents of the named fixtures into the database.
    See the `Django documentation
    <https://docs.djangoproject.com/en/5.0/ref/django-admin/#loaddata>`__.

    With a :term:`Lino application` you will probably prefer :manage:`initdb` or
    :cmd:`pm prep`.


.. management_command:: migrate

    Updates the database schema.

    With a :term:`Lino application` you will probably prefer :cmd:`pm dump2py`
    as explained in :doc:`datamig`.
