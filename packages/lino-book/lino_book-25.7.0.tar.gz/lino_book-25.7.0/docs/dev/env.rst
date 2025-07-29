.. _dev.setup:
.. _dev.env:

=====================================
More about your developer environment
=====================================

.. contents::
    :depth: 1
    :local:


Introducing atelier
===================

..
  The word **project** is used for quite a lot of things. There are many types of
  "projects".  For example a **Django project** is a directory where you can
  invoke a :manage:`runserver`.  It contains at least a :xfile:`settings.py` and
  usually a file :xfile:`manage.py`. We call such a directory a :term:`Lino site`.

As a Lino developer you are going to use :mod:`atelier`, a minimalist
developer project management tool. A "project", for atelier, is any directory
containing at least a file :xfile:`tasks.py`.

You "activate" a project by opening a terminal and changing to its directory.
That's all. Almost all. Read on.

- An atelier project usually corresponds to a public code repository
  (using Git or Mercurial). But you can have unpublished projects
  that have no repo at all.
- One atelier project can contain one or more :term:`demo projects <demo project>`.
- An atelier project usually corresponds to a given Python package to
  be published on PyPI.
- An atelier project can have a number of Sphinx document trees
  (default is one tree named :file:`docs`).

The :xfile:`tasks.py` file in your project directory is comparable to a
:file:`Makefile` or a :file:`package.json`, it defines instructions used during
development. These instructions are run using the :cmd:`inv` command. The
:cmd:`inv` command comes from the `invoke
<https://www.pyinvoke.org/index.html>`__ Python package, which gets installed by
:mod:`atelier`, which gets installed when you :doc:`install a developer
environment </dev/install/index>`.

.. command:: inv

  Run one of the instructions available

You can say :cmd:`inv -l` to see a list of available tasks::

  $ inv -l
  Available tasks:

    bd               Build docs. Build all Sphinx HTML doctrees for this project.
    blog             Edit today's blog entry, create an empty file if it doesn't yet exist.
    check            Check configuration integrity.
    ci               Checkin and push to repository, using today's blog entry as commit message.
    clean            Remove temporary and generated files.
    cov              Run all tests and create a coverage report.
    ct               Print all today's commits to stdout.
    install          Install required Python packages to your Python environment and/or
    mm               Extract messages, then initialize and update all catalogs.
    pd               Publish docs. Upload docs to public web server.
    pepper           Run PEP formatting and checking.
    prep             Run preparation tasks that need to run before testing.
    pull             Pull latest changes, including those from upstream if there is one.
    readme           Generate or update `README.txt` or `README.rst` file from `SETUP_INFO`.
    register         Register this project (and its current version) to PyPI.
    release          Publish a new version to PyPI.
    run              Run a given python script on all the demo projects.
    sdist            Create a source distribution.
    test             Run the test suite of this project.
    test-sdist       Install a previously created sdist into a temporary virtualenv and
    updatefixtures


Your atelier projects don't need to be under a single base directory. You
will have different project base directories.   One of them is
:xfile:`~/lino/lino_local`, but another one is :xfile:`~/lino/env/repositories`:

.. xfile:: ~/lino/env/repositories

  The base directory for every repository you cloned from GitLab.


Configuring atelier
===================

To finish the installation of your Lino developer environment, you must create
your  :xfile:`~/.atelier/config.py` file. You must create this file yourself,
manually::

  $ mkdir ~/.atelier
  $ nano ~/.atelier/config.py

Add the following content:

.. literalinclude:: atelier_config_example.py
  :lines: 10-

The atelier config file tells :mod:`atelier` the list of your projects. Letting
:mod:`atelier` know where your projects are has the advantage that you can run
the :cmd:`per_project` script (or its alias :cmd:`pp`) to run a given command
over many projects.

..
  You can use :mod:`rstgen.sphinxconf.interproject` to create
  intersphinx links from one project's docs to the docs of another
  project.


Usage examples
==============

You can now play around in your environment.

See a list of your atelier projects::

    $ pp -l
    ========= ========= ==========================================
     Project   Status    URL
    --------- --------- ------------------------------------------
     lino      master!   http://www.lino-framework.org
     xl        master    http://www.lino-framework.org
     noi       master    http://noi.lino-framework.org
     cosi      master    http://cosi.lino-framework.org
     avanti    master    http://avanti.lino-framework.org/
     vilma     master    http://vilma.lino-framework.org
     care      master    http://care.lino-framework.org
     tera      master    http://tera.lino-framework.org
     book      master!   http://www.lino-framework.org
     voga      master    http://voga.lino-framework.org
     welfare   master    https://welfare.lino-framework.org
     amici     master    http://amici.lino-framework.org
    ========= ========= ==========================================


Change to :file:`~/lino/env/repositories/lino` and download the latest version
of Lino::

  $ go lino
  $ git pull

Do the same for all your cloned repositories::

  $ pp git pull

Run the full test suite in :ref:`book`::

  $ go book
  $ inv prep test

(:cmd:`inv prep test` is equivalent to :cmd:`inv prep` followed by :cmd:`inv
test`.)

Build a local copy of the Lino Developer Guide::

  $ go book
  $ inv bd

Afterwards you can start your browser on the generated output::

  $ python -m webbrowser docs/.build/index.html

Building the docs might not work out of the box, it is a topic of its own.  See
:doc:`/dev/builddocs`.

It happens that I type the following before leaving my computer for
getting a cup of coffee::

  $ pp inv prep test bd

Which is: in each Lino repository, run :cmd:`inv prep` followed by :cmd:`inv
test` followed by :cmd:`inv bd`.


Bash aliases installed by getlino
=================================

Remember that a file :xfile:`~.lino_bash_aliases` was created in
:doc:`/dev/install/index` and we asked you to source it from within your
:xfile:`~/.bash_aliases` or :xfile:`~/.bashrc` file.

.. xfile:: ~/.lino_bash_aliases

  Contains several aliases and shell functions.

  When installing Lino on a :term:`production server` it is a system-wide file
  in :file:`/etc/getlino/lino_bash_aliases`.

The following command aliases are installed by :xfile:`~/.lino_bash_aliases`:

.. command:: go

  :cmd:`cd` to one of your local project directories using its nickname.

  In case you also use the `Go <https://golang.org/>`_ programming language on
  your computer, you should obviously edit your pick another name than "go".

The :cmd:`go` command is a shell function in your :xfile:`~/.lino_bash_aliases`
and looks like this::

  function go() {
      for BASE in ~/lino/lino_local ~/lino/env/repositories ~/lino/env/repositories/book/lino_book/projects
      do
        if [ -d $BASE/$1 ] ; then
          cd $BASE/$1;
          return;
        fi
      done
      echo Oops: no project $1
      return -1
  }

So there are three "types" of nicknames::

  $ go lino   #  cd ~/lino/env/repositories/lino
  $ go first  #  cd ~/lino/lino_local/first
  $ go min1   #  cd ~/lino/env/repositories/book/lino_book/projects/min1

Note how the ``for BASE in`` of the :cmd:`go` command also loops over the
directory :file:`~/lino/env/repositories/book/lino_book/projects`. This
directory contains our :term:`demo projects <demo project>`.


.. command:: runserver

  An alias for ``LINO_LOGLEVEL=DEBUG python manage.py runserver``

.. command:: pm

  An alias for ``python manage.py``, in other words for executing a
  :cmd:`django-admin` command.

  This alias is installed by :cmd:`getlino configure`.

.. command:: a

  Expands to ``. env/bin/activate``.

  This alias is installed by :cmd:`getlino configure`.

.. command:: pywhich

    Shortcut to quickly show where the source code of a Python module
    is coming from.

    This is useful e.g. when you are having troubles with your virtual
    environments.

The :cmd:`pywhich`  command is actually also a simply shell function::

  function pywhich() {
    python -c "import $1; print($1.__file__)"
  }


.. We chose ``env`` for our environment. You are free to choose any
   other name for your new environment, but we recommend this
   convention because it is being used also on production servers.
   Note that :xfile:`env` might be a *symbolic-link* pointing to some
   shared environment folder.


How to change the location of your repositories
===============================================

The following it not much tested. Read and follow at your own risk or together
with your mentor.

Imagine that for some reason you want to trash your :term:`virtualenv` and
create it anew. The longest waiting time when you installed your developer
environment was to download all the repositories from GitLab. You can avoid
downloading them again by moving your repositories to another location and to
inform getlino about it by saying  :option:`getlino configure --repos-base`::

  $ mv ~/lino/env/repositories ~/
  $ getlino configure --repos-base ~/repositories

The :cmd:`getlino` command has a quite primitive user interface. But it is less
stupid that the first impression might leave. For example it knows that it has
been run before::

  This is getlino version 24.3.0 running on Ubuntu 22.04.4 LTS (ubuntu jammy).
  This will write to configuration file /home/luc/.getlino.conf

Basically you just answer :kbd:`ENTER` to every question, or :kbd:`y` when
:kbd:`ENTER` doesn't continue. Sometimes you can skip a step by answering
:kbd:`n`, for example when it asks to "run sudo apt-get update -y;sudo apt-get
upgrade -y;" and you know that you did that recently.

You will also see that the answer to the question about `repos_base` is set to
what you specified at the command-line::

  - repos_base (Base directory for shared code repositories) [~/repositories]:

At some moment you should see::

  Clone repositories to /home/luc/work ? [y or n] Yes
  No need to clone atelier : directory exists.
  No need to clone etgen : directory exists.
  No need to clone eid : directory exists.
  No need to clone cd : directory exists.
  No need to clone getlino : directory exists.
  No need to clone lino : directory exists.
  No need to clone xl : directory exists.
  No need to clone welfare : directory exists.
  No need to clone react : directory exists.
  No need to clone openui5 : directory exists.
  No need to clone book : directory exists.
  No need to clone cg : directory exists.
  No need to clone ug : directory exists.
  No need to clone hg : directory exists.
  No need to clone lf : directory exists.
  No need to clone ss : directory exists.
  No need to clone algus : directory exists.
  No need to clone amici : directory exists.
  No need to clone avanti : directory exists.
  No need to clone cms : directory exists.
  No need to clone care : directory exists.
  No need to clone cosi : directory exists.
  No need to clone mentori : directory exists.
  No need to clone noi : directory exists.
  No need to clone presto : directory exists.
  No need to clone pronto : directory exists.
  No need to clone tera : directory exists.
  No need to clone shop : directory exists.
  No need to clone vilma : directory exists.
  No need to clone voga : directory exists.
  No need to clone weleup : directory exists.
  No need to clone welcht : directory exists.

..
  .. xfile:: install_dev_projects.sh

  Not much tested. Read and follow at your own risk.

  Here is how to quickly install the Lino SDK into a new virtualenv::

    $ cd ~/lino/env/repositories
    $ sh book/docs/dev/install_dev_projects.sh

  Automated way for cloning and installing the code repositories::

    $ cd ~/lino/env/repositories
    $ wget https://raw.githubusercontent.com/lino-framework/book/master/docs/dev/install_dev_projects.sh
    $ sh install_dev_projects.sh


How to switch to the development version of atelier
===================================================

This section is not needed and not much tested. Read and follow at your own
risk.

The :mod:`atelier` package had been automatically installed together
with :mod:`lino`. That is, you are using the *PyPI* version of
Atelier.  That's usually okay because Atelier is more or less
stable. But one day we might decide that you should rather switch to
the *development* version.

Doing this is theoretically easy. Uninstall the PyPI version and then install
the development version::

  $ pip uninstall atelier

  $ cd ~/lino/env/repositories
  $ git clone https://github.com/lino-framework/atelier.git
  $ pip install -e atelier


How to send emails from your developer environment
==================================================

The demo sites of a developer environment don't send any emails to the outside
world. The test suite uses different techniques to simulate sending emails. But
even as a Lino developer you might want to really send emails. For example when
you develop or debug some action that sends emails and you want to really send
them out. Or maybe you run your own :term:`production site` on your developer
machine.

The related Django settings (for example :setting:`EMAIL_HOST_USER` and
:setting:`EMAIL_HOST_PASSWORD`) contain information that only you can give.  And
you don't want to accidentally publish them. This is why you want to store them
in your :term:`local settings module`.

Note that not all :term:`demo projects <demo project>` use the :term:`local
settings module`. Only those which have the following lines in their
:xfile:`settings.py` file::

  try:
      from lino_local.settings import *
  except ImportError:
      pass


The local settings module
=========================

Your :term:`local settings module` has been created by :cmd:`getlino configure`
in file :file:`~/lino/lino_local/settings.py`.

If you want Lino to find it, you need to set :setting:`PYTHONPATH` to
:file:`~/lino`. For example by adding the following line to your
:xfile:`.bashrc` file::

  export PYTHONPATH=/home/joe/lino

On a :term:`production server` or for sites created with :cmd:`getlino
startsite` you don't need to set :setting:`PYTHONPATH` because the
:xfile:`manage.py` script of these sites contains a line ``sys.path.insert(0,
'/usr/local/lino')``.


Using the console email backend
===============================

Rather than actually sending out emails, you might prefer to simply see them on
the console. You can achieve this by setting :setting:`EMAIL_BACKEND` as
follows::

  EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

With that setting you can copy the console output to a file :xfile:`tmp.eml` and
then opene this file in Thunderbird.
