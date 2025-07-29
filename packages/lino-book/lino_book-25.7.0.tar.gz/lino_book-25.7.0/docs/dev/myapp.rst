.. _dev.myapp:

======================================
How to write your own Lino application
======================================

Just in case you feel ready to start your own Lino application, here is how to
do it. But you may leave this section for later. And don't panic if you get
stuck.

- Find a **verbose name** for your application. Something like :ref:`cosi`,
  :ref:`avanti`, :ref:`tera`, :ref:`voga`, ... The application name should
  identify your application so that its users can talk about it. Consult
  :doc:`/apps` for a list of names that are already taken.

- Find a **nickname**. The nickname is what you as the developer are going to
  type often. It must be unique in your developer environment.

- Find the **code name** of the Python package that will hold your application.
  Consult `PyPI <https://pypi.org/search/?q=lino_&o=>`__ for a list of code
  names that are already taken.

  For example, the code name for "Lino Così" is :mod:`lino_cosi`.

- Run :cmd:`getlino startproject`::

    cd ~/repositories
    getlino startproject NICKNAME

- Answer the questions
