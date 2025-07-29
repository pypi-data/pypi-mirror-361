.. _src.lino.api:

=================
``lino.api``
=================

.. toctree::
    :maxdepth: 1

    ad/index
    dd/index
    rt/index

The :mod:`lino.api` package contains a series of modules that encapsulate Lino's
core functionalities.  They don't define anything on their own but just import
things that are commonly used in different contexts. One module for each of the
three startup phases used when writing application code:

- :doc:`ad/index` contains classes and functions that are available
  already **before** your Lino application gets initialized.  You use
  it to define your **overall application structure** (in your
  :xfile:`settings.py` files and in the :xfile:`__init__.py` files of
  your plugins).

- :doc:`dd/index` is for when you are **describing your database schema** in
  your :xfile:`models.py` modules.

- :doc:`rt/index` contains functions and classes that are commonly used "at
  runtime", i.e. when the Lino application has been initialized. You may
  *import* it at the global namespace of a :xfile:`models.py` file, but you can
  *use* most of it only when the :func:`startup` function has been called.

Recommended usage is to import these modules as follows::

  from lino.api import ad, dd, rt, _
