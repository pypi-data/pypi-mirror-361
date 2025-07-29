========
Features
========

.. _lino.features:

Lino is a framework within the Django framework.
It enters Django through your :xfile:`settings.py` file.
Deploying a :term:`Lino site` is like `deploying a Django project
<https://docs.djangoproject.com/en/5.0/howto/deployment/>`__.

But an application, in Lino, is much more than what Django calls an
"application". A Lino application is an out-of-the box Django project. Because
Lino applications are Django projects, the well-known Django features also apply
to Lino:

- You define your **database models** `as in Django
  <https://docs.djangoproject.com/en/5.0/topics/db/models/>`__

- **Internationalization** works `as in Django
  <https://docs.djangoproject.com/en/5.0/topics/i18n/translation/>`__

Lino then adds its own features to the above:

- An out-of-the-box :term:`front end`.  Application developers should focus on
  data structures and applications logic, not waste their time writing HTML,
  JavaScript or CSS. (Nothing against the developers of these technologies! Lino
  relies on their work!)

  :doc:`Separate business logic and front end <ui>` is one
  of Lino's design goals.

- :ref:`Layouts <layouts>`:
  Lino applications use the Python language not only
  for designing your *models* but also your *forms*.

- With Lino you define also your
  :ref:`permissions <permissions>` and :ref:`workflows <workflows>` in Python.

- Lino applications have a good support for managing
  :ref:`multilingual database content <mldbc>`.

- Lino provides tools for generating :ref:`multilingual end-user documentation
  <userdocs>`.

- Lino includes :ref:`dpy`, a great alternative to `Django's built-in
  migration system
  <https://docs.djangoproject.com/en/5.0/topics/migrations/>`_ to
  manage your :ref:`database migrations <datamig>`.

- Lino comes with a nice way for handling :ref:`polymorphism`.

- Lino includes :ref:`xl`, a collection of reusable plugins for all
  kinds of Lino applications.
