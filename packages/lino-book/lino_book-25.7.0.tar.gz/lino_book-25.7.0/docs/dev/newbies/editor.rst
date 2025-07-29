.. _dev.editor:

===================
Which editor to use
===================

Software developers spend most of their working time with a :term:`source code`
editor.

Text editors like `joe <https://en.wikipedia.org/wiki/Joe%27s_Own_Editor>`__ or
`nano <https://www.nano-editor.org/>`__ are good for occasional changes in files
on a server that you access via a terminal, but they are not designed for
jumping back and forth in a repository with thousands of source code files.

If you haven't yet made up your choice about which editor to use, then we
recommend to start with Pulsar.  See the next section. There are other choices,
see `Python editors <https://wiki.python.org/moin/PythonEditors>`__ and and
`IntegratedDevelopmentEnvironments
<https://wiki.python.org/moin/IntegratedDevelopmentEnvironments>`__.


.. _atom:

Getting started with Pulsar
===========================

Follow the installation instructions on https://pulsar-edit.dev

Once in Pulsar, you should install two packges: `atom-ide-base
<https://github.com/atom-community/atom-ide-base>`__ and `pulsar-ide-python
<https://web.pulsar-edit.dev/packages/pulsar-ide-python>`__.

..
  and configure its "Path to
  Python directory" to point to your :term:`default environment` (which you
  installed in :doc:`/dev/install/index`).

Select :menuselection:`File --> Add project folder...` and add your
:xfile:`~/lino` directory. This will cause Pulsar to index all files below this
directory.

..
  How to instruct Pulsar to use your :term:`default environment` when doing syntax
  checks or finding definitions:

  - Select :menuselection:`Edit --> Preferences --> Packages`

  - Select the settings of the python-tools plugin

  - Set the :guilabel:`Path to Python directory` field to :file:`~/lino/env/bin`
    (or whatever your chose as your :term:`default environment`).

Some useful keyboard shortcuts:

- :kbd:`Ctrl+P` open an existing file using fuzzy file name search within all files of the project.
- :kbd:`Shfit+Ctrl+F` find (and optionally replace) a text string in all files (or in some)
- :kbd:`Alt+Q` reflow selection
- :kbd:`Ctrl+Alt+O` go to definition


In the ``pulsar-ide-python`` settings,

- change line length from 79 to 88
- Set the `Ignore` field to the following value::

    E121, E123, E126, E226, E24, E704, F403, W503, W504

Discussion about some of these warnings:

- `F403 <https://www.flake8rules.com/rules/F403.html>`__  (`from module import *
  used; unable to detect undefined names`). See :ticket:`5966` (Should we stop
  using from .ui import \*?)

- `E501 <https://www.flake8rules.com/rules/E501.html>`__ (line too long)  caused
  :ticket:`5965` (SyntaxError: unterminated string literal)
