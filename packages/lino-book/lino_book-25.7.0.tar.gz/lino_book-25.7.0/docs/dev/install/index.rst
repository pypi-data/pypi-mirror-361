.. _user.install:
.. _getlino.install.dev:
.. _lino.dev.install:
.. _dev.install:
.. _getlino.install.contrib:
.. _contrib.install:

=========================================
Install your Lino developer environment
=========================================

.. _invoke: http://www.pyinvoke.org/
.. _atelier: http://atelier.lino-framework.org/
.. _pycrypto: https://pypi.python.org/pypi/pycrypto

.. highlight:: console

This document describes how to install a Lino :term:`developer environment` on
your computer.

.. glossary::

  developer environment

    A set of tools installed on your computer so you can develop your own
    :term:`Lino application` or otherwise contribute to Lino as a developer.


.. contents::
    :depth: 1
    :local:

.. _lino.dev.env:

Set up a virtual Python environment
===================================

In order to keep Lino separate from your system-wide Python, you will first
install a :term:`virtualenv` and then install Lino into this environment.

.. glossary::

  virtualenv

    A virtual Python environment. A directory tree containing a stand-alone
    Python installation where you can install and remove packages without
    modifying your computer system's Python installation.

..
  If virtualenvs are new to you: some reasons for creating a new environment:

  - other software on your computer might require different Python packages than
    those required by Lino, and there is the chance of version or dependency
    conflicts.

  - if you wish to remove Lino from your system you only need to remove the
    virtual environment rather than trying to remove Lino's dependencies from the
    system environment without breaking any other programs that use python.

If you haven't yet used virtualenvs, you must first install the feature::

  $ sudo apt-get install python3-venv  # Debian
  $ sudo dnf install python3-virtualenv  # RedHat

We suggest to install your :term:`developer environment` under :file:`~/lino`,
so here we go::

  $ mkdir ~/lino
  $ python3 -m venv ~/lino/env
  $ . ~/lino/env/bin/activate

The dot (``.``) is a synonym for the :cmd:`source` command. If you
didn't know it, read the `manpage
<http://ss64.com/bash/source.html>`__ and `What does 'source' do?
<http://superuser.com/questions/46139/what-does-source-do>`__

One last thing before we actually install Lino into that virtualenv: as a
developer you probably don't want to type ``. ~/lino/env/bin/activate`` each
time you open a new terminal, so you should set it as your :term:`default
environment`.

.. glossary::

  default environment

    The default :term:`virtualenv` you use when developing.


Please add the following line to your :file:`~/.bashrc` file in order to define
your :term:`default environment`::

      source ~/lino/env/bin/activate

..
  Instruct your favourite :doc:`code editor </dev/newbies/editor>` to use this
  :term:`default environment` when doing syntax checks or finding definitions.


Install and run :ref:`getlino`
==============================

Now that your :term:`default environment` is activated, let's install
:ref:`getlino`::

  $ pip install getlino

Now run :cmd:`getlino configure` with the following options::

  $ getlino configure --clone --devtools --appy

.. $ getlino configure --clone --devtools --redis

It asks a lot of questions, but you can hit :kbd:`ENTER` for each of them.
When it does not react to :kbd:`ENTER` but asks a ``[y or n]`` question, then
make sure to read the question and understand it before you hit :kbd:`y`. For
details about each question or if something doesn't work as expected, see
Troubleshooting_ below or the documentation about :ref:`getlino`.

The process of cloning the repositories takes some time. Lino is a whole little
collection of repositories and applications!  See :doc:`/about/overview` if you
are curious. You don't need to dive into each of them right now, but you must at
least *install* them so that your environment is complete.

When getlino has finished, add manually the following line to your
:xfile:`.bashrc` file::

  source ~/.lino_bash_aliases

The :xfile:`~/.lino_bash_aliases` file installs several shell commands, we will
have a deeper look at them in :doc:`/dev/env`.

Is Lino installed?
==================

A quick test when you want to see whether Lino is installed is to say
"hello" to Lino:

.. py2rst::

   self.shell_block(["python", "-m", "lino.hello"])

Python's `-m <https://docs.python.org/3/using/cmdline.html#cmdoption-m>`_
command-line switch instructs it to just *import* the specified module (here
:mod:`lino.hello`) and then to return to the command line.

.. Here is the same as a tested code snippet:

  >>> from atelier.sheller import Sheller
  >>> shell = Sheller()
  >>> shell("python -m lino.hello")  #doctest: +ELLIPSIS
  Lino ..., Django ..., Python ..., Babel ..., Jinja ..., python-dateutil ...


Run a demo project
==================

A Lino :term:`developer environment` comes with a lot of :term:`demo projects
<demo project>`.

.. glossary::

  demo project

    A directory with at least two files :xfile:`settings.py` and
    :xfile:`manage.py`, which define a  :term:`Django project directory` (a
    :term:`Lino site`) that can be used for testing, demonstrating and
    explaining Lino.

Please try one of the demo projects::

  $ go polly  # alias for: cd ~/lino/repositories/book/lino_book/projects/polly
  $ pm prep --noinput  # alias for: python manage.py prep --noinput
  $ runserver  # alias for: python manage.py runserver

Point your browser to http://localhost:8000 and you should see something like
the following:

.. image:: polly.png
  :width: 90%

If you get this screen, then you can head over to the next page.

Otherwise you are going to learn a bit more :-)
The following Troubleshooting_ section will maybe help you.
And keep in mind that this is a reason to ask for support from your mentor because
your problem will probably help us
to make Lino and this Developer Guide a bit better.


Troubleshooting
===============

``polly`` is the nickname of a :term:`demo project`.
We will discover more demo projects in :doc:`/discover`.

Before starting a development server on a demo project for the first time, you
must initialize its database using the :cmd:`pm prep` command.

The shell commands :cmd:`go`, :cmd:`pm` and :cmd:`runserver` are defined by the
:file:`~/.lino_bash_aliases` file.

Note the difference between :cmd:`inv prep` and the :cmd:`pm prep` command.
:cmd:`inv prep` runs the :cmd:`pm prep` command for each demo project of a
repository.  The demo projects of a repository are declared in the
:xfile:`tasks.py` file. You can run the :cmd:`pm prep` command for all demo
projects by going to the root directory of the book project and saying :cmd:`inv
prep`::

  $ go book   # alias for: cd ~/lino/env/repositories/book
  $ inv prep

More about getlino
------------------

The getlino script does a lot of work. These commands take some time when you
run them the first time on your machine because they will download and install
all Python packages needed by Lino.  If you install them a second time into
another environment, the process will be quicker because pip caches the
downloaded packages.

``languages (The languages to set on new sites) [en]:``
This is just the default value that getlino will put for :attr:`languages
<lino.core.site.Site.languages>` in the :xfile:`settings.py` of new sites.

In some circumstances getlino will say "The following command was not executed
because you cannot sudo", followed by an "apt-get install" command. Consider
running these commands manually.

In case you have used getlino on your machine before (maybe in another
:term:`virtualenv`, but on the same machine), then you might want to delete your
configuration files before installing again::

  $ rm ~/.getlino.conf
  $ sudo rm /etc/getlino/getlino.conf

The ``--appy`` option tells :cmd:`getlino configure` to install a LibreOffice
server on your machine. Some of the demo examples use :mod:`lino_xl.lib.appypod`
for producing printable pdf files.  That's why you need a LibreOffice server on
your system. Details about what getlino does are described in :ref:`admin.oood`.


More about virtualenvs
----------------------

Using virtual environments can be a challenge. Here are some diagnostic tricks.

You can **deactivate** a virtual environment with the command
:cmd:`deactivate`.  This switches you back to your machine's
system-wide environment.

You can **switch to another** virtualenv simply by activating it, you
don't need to deactivate the current one first.

You should never **rename** a virtualenv (they are not designed for
that), but you can easily create a new one and remove the old one.

To learn more, read Dan Poirier's post `Managing multiple Python
projects: Virtual environments
<https://www.caktusgroup.com/blog/2016/11/03/managing-multiple-python-projects-virtual-environments/>`__
where he explains what they are and why you want them.

After creating a new environment, you should always update `pip` and
`setuptools` to the latest version::

  $ pip install -U pip setuptools
  Collecting pip
    Using cached https://files.pythonhosted.org/packages/43/84/23ed6a1796480a6f1a2d38f2802901d078266bda38388954d01d3f2e821d/pip-20.1.1-py2.py3-none-any.whl
  Collecting setuptools
    Downloading https://files.pythonhosted.org/packages/8e/11/9e10f1cad4518cb307b484c255cae61e97f05b82f6d536932b1714e01b47/setuptools-49.2.0-py3-none-any.whl (789kB)
      100% |████████████████████████████████| 798kB 1.1MB/s
  Installing collected packages: pip, setuptools
    ...
  Successfully installed pip-20.1.1 setuptools-49.2.0


How to see which is your current :term:`virtualenv`::

    $ echo $VIRTUAL_ENV
    /home/joe/lino/env

    $ which python
    /home/joe/lino/env/bin/python

How to see what's installed in your current virtualenv::

    $ pip freeze

The output will be about 60 lines of text, here is an excerpt::

    alabaster==0.7.9
    appy==0.9.4
    argh==0.26.2
    ...
    Django==1.11.2
    ...
    future==0.15.2
    ...
    -e git+git+ssh://git@github.com/lino-framework/lino.git@91c28245c970210474e2cc29ab2223fa4cf49c4d#egg=lino
    -e git+git+ssh://git@github.com/lino-framework/book.git@e1ce69aaa712956cf462498aa768d2a0c93ba5ec#egg=lino_book
    -e git+git+ssh://git@github.com/lino-framework/noi.git@2e56f2d07a940a42e563cfb8db4fa7444d073e7b#egg=lino_noi
    -e git+git@github.com:lino-framework/xl.git@db3875a6f7d449490537d68b08daf471a7f0e573#egg=lino_xl
    lxml==3.6.4
    ...
    Unipath==1.1
    WeasyPrint==0.31
    webencodings==0.5


The `-e <https://pip.pypa.io/en/latest/reference/pip_install.html#cmdoption-e>`_
command-line switch for :command:`pip` causes it to use the "development" mode.
The first argument after ``-e`` is not a *project name* but a path to a
*directory* of your local filesystem. Development mode means that these modules
run "directly from source".  `pip` does not *copy* the sources to your Python
`site_packages`, but instead adds a link to them.
