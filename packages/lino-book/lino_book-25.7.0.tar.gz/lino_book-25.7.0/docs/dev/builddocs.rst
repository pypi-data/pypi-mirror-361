.. doctest docs/dev/builddocs.rst
.. _lino.dev.bd:

======================
Building the Lino docs
======================

This page explains how to build the Lino docs, i.e. how to generate for example
the html pages you are reading right now. We assume that you have read
:ref:`ug.topics.docs`.

.. contents::
  :local:
  :depth: 1

Theoretically it's easy
=======================

A Lino :term:`documentation tree` is *static* html built from a series of Sphinx
:term:`source files <source code>` before it is uploaded to some web server.

When your development environment is correctly installed as explained in
:doc:`install/index`, then --theoretically-- it's easy to build a Lino
:term:`doctree`: you just run :cmd:`inv bd` in the root directory of its
repository::

  $ go books
  $ pip install -r requirements.txt
  $ inv bd

This will tell Sphinx to read the :file:`.rst` source files and to generate
:file:`.html` files into the :file:`docs/.build` directory.

You can now start your browser on the generated files::

  $ python -m webbrowser docs/.build/html/index.html

If you get some error message, then you need to read the Troubleshooting_
section.

If the doctree has :envvar:`use_dirhtml` set to `True`, then the navigation in
your local doctree won't work perfectly.


Introducing Sphinx
==================

Lino makes heavy usage of **Sphinx**, the dominant documentation
system in the Python world.  Sphinx is a tool that "makes it easy to
create intelligent and beautiful documentation" and that "actually
makes programmers **want** to write documentation!"
(`www.sphinx-doc.org <https://www.sphinx-doc.org>`__).

For example, the "source code" of the page your are reading right now
is in a file `docs/dev/builddocs.rst
<https://github.com/lino-framework/book/blob/master/docs/dev/builddocs.rst>`__.

Read more about the markup used by Sphinx in `reStructuredText
<https://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html>`_.
Also `Configuration <https://www.sphinx-doc.org/en/master/usage/configuration.html>`_.


Troubleshooting
===============

.../docs/api/xxx.yyy.foo.rst:21:failed to import Bar
----------------------------------------------------

This can occur when you have an earlier build of the book on your
computer, then pulled a new version of some Lino repository (or made
some local code changes) and then run :cmd:`inv bd` again.

The error should disappear either if you manually remove the specified
file :file:`docs/api/xxx.yyy.foo.rst`.  Or, most fool-proof solution,
you use the :cmd:`inv clean` command to automatically remove cached
and generated files::

    $ inv clean -b


[autosummary] failed to import 'lino.modlib.users.models'
----------------------------------------------------------------------------

This means that `autosummary
<https://www.sphinx-doc.org/en/master/usage/extensions/autosummary.html>`__ (which
in turn needs `autodoc
<https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html>`__) has a
problem to import the module
:mod:`lino.modlib.users.models`.

Indeed you can verify that importing this module in a normal Python
session will fail:

.. Make sure that DJANGO_SETTINGS_MODULE isn't set because otherwise Django
   raises another exception:

   >>> import os ; u = os.environ.pop('DJANGO_SETTINGS_MODULE', None)

>>> import lino.modlib.users.models  #doctest: +NORMALIZE_WHITESPACE +IGNORE_EXCEPTION_DETAIL +ELLIPSIS
Traceback (most recent call last):
...
ImproperlyConfigured: Requested setting SITE, but settings are not configured. You must either define the environment variable DJANGO_SETTINGS_MODULE or call settings.configure() before accessing settings.

As the error message tries to explain, the module refuses to import because
:envvar:`DJANGO_SETTINGS_MODULE` is not set.  That's related to a well-known
oddness of Django: you cannot simply import a module that imports :mod:`django`
when that environment variable is not set.

Note that the :file:`docs/conf.py` contains (among others) the following lines::

    from lino.sphinxcontrib import configure
    configure(globals(), 'lino_book.projects.min9.settings')

This calls the :func:`lino.sphinxcontrib.configure` function, which basically
does exactly what we need here: it sets the :envvar:`DJANGO_SETTINGS_MODULE` to
:mod:`lino_book.projects.min9.settings`.

So Sphinx activates the :mod:`lino_book.projects.min9` project when generating
the docs.

But your message says that something went wrong during all this.

Let's try this::

    $ # cd to ~/lino/env/repositories/book/lino_book/projects/min9:
    $ go min9
    $ python manage.py shell

And in *that* Python shell you try to import the that which Sphinx
was not able to import::

    import lino.modlib.users.models

Now you should see a traceback, and that traceback can help you to find the
actual problem.




Let's play
==========

Let's play a bit:

Open the source file of this page::

  $  nano docs/dev/builddocs.rst

Edit something in that file and save your changes. Then build the book
again::

  $ inv bd

Then hit :kbd:`Ctrl-R` in your browser and check whether the HTML
output changes as expected.

You can undo all your local changes using::

  $ git checkout docs/team/builddocs.rst

Or, if you agree to :doc:`contribute <contrib>` your changes to the Lino
project, you can :doc:`submit a pull request <request_pull>` as you would do
with code changes.
