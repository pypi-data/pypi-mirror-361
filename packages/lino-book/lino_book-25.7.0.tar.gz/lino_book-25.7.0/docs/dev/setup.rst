.. doctest docs/dev/setup.rst
.. _dev.setup_info:

====================================
How Lino applications use `setup.py`
====================================

This document is obsolete after :ticket:`5484`  (Migrate from setup.py to
pyproject.toml).

It describes our trick for keeping the metadata about a Python package in a
single place.  It does not depend on Lino and we recommend it for any Python
project which contains a package.

The classical layout is to store the setup information directly in the
:xfile:`setup.py` file of your project. The problem with this layout is that the
:xfile:`setup.py` file is not available at runtime.

For example the **version number**. You need it of course in the
:xfile:`setup.py`, but there are quite some projects that want to show somehow
their version.  So they need it at runtime as well.  And that number can change
quickly and can be critical. You don't want to store it in two different places.

Is there a way to have setup information both in a central place *and**
accessible at runtime?

It is an old problem, and e.g. `Single-sourcing the package version
<https://packaging.python.org/guides/single-sourcing-package-version/>`__
describes a series of answers.


Our solution
============

To solve this problem, we store the setup information in a separate file, which
we usually name :xfile:`setup_info.py` and which we load from both our
:xfile:`setup.py` and our packages's main :xfile:`__init__.py` file. The
:xfile:`setup.py` loads it using the :func:`exec` function while the packages's
main :xfile:`__init__.py` file can simply import it.

That's why the :xfile:`setup.py` of a package "xxyyzz" contains just this::

    from setuptools import setup
    fn = 'xxyyzz/setup_info.py')
    with open(fn, "rb") as fd:
        exec(compile(fd.read(), fn, 'exec'))
    if __name__ == '__main__':
        setup(**SETUP_INFO)

And the :file:`__init__.py` file of the main module contains this::

    from os.path import join, dirname
    from setup_info import SETUP_INFO
    __version__ = SETUP_INFO.get('version')


Usage examples::

  >> from lino import SETUP_INFO
  >> print(SETUP_INFO['description'])
  A framework for writing desktop-like sustainably free web applications using Django and ExtJS or React

  >> from lino_xl import SETUP_INFO
  >> print(SETUP_INFO['description'])
  The Lino Extensions Library

Related files
=============

These are the files we are talking about here.

.. xfile:: setup.py

    A file named :xfile:`setup.py` is part of the `minimal structure
    <https://python-packaging.readthedocs.io/en/latest/minimal.html>`__
    of every Python project.  It is in the root directory of a project
    and contains information about the project, e.g. the **version
    number** or the **dependencies** (i.e. which other Python packages
    must be installed when using your package). The information in
    this file is used for running test suites, installing the project
    in different environments, etc...


.. xfile:: setup_info.py

    The file that *actually* contains the information for Python's
    :xfile:`setup.py` script. It is loaded (or imported) from both the :xfile:`setup.py`
    and the packages's main :xfile:`__init__.py` file and usually defines a
    global variable `SETUP_INFO`, a dict of keyword arguments to be passed to
    the :func:`setup` function. It is located in the directory that contains
    the main package of your project. E.g. for the :ref:`xl` project it is in
    :file:`lino_xl/setup_info.py`.  the main package of a project is specified
    in the :xfile:`tasks.py`.

.. xfile:: MANIFEST.in

    TODO

.. xfile:: test_packages.py

    A file in the test suite of a repository that runs :meth:`run_packages_test
    <atelier.test.TestCase.run_packages_test>`.

Setup information
=================

The :func:`setup` function has a lot of keyword parameters, which are documented
elsewhere.

.. glossary::

  install_requires

    See http://python-packaging.readthedocs.io/en/latest/dependencies.html

  tests_require

    See http://python-packaging.readthedocs.io/en/latest/dependencies.html

  description

    A terse plain-text description of the package. Usually a single sentence and
    no period at the end.

    For applications known by :mod:`getlino` this is also listed on
    :ref:`getlino.apps`.

  long_description

    A longer description to be published on PyPI.

    May contain reStructuredText formatting, but no Sphinx-specific additions.


How to suggest changes to a README file
=======================================

The :term:`long_description` in the :xfile:`setup_info.py` file is also used by
:cmd:`inv bd` as the source text for generating the project's
:xfile:`README.rst`.


We assume that you have installed a development environment as explained in
:ref:`dev.install`.

Open the :xfile:`setup_info.py` file of your project and find the
`long_description`.

Edit its content.

Run :cmd:`inv bd` in the root directory of the project.  This will ask you::

    Overwrite /path/to/my/project/README.rst [Y,n]?

Hit :kbd:`ENTER`.

Open the :xfile:`README.rst` file and check that it contains your changes.

Submit a pull request with the two modified files :xfile:`setup_info.py` and
:xfile:`README.rst`.
