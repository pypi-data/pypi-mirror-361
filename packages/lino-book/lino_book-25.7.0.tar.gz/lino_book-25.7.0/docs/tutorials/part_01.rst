.. _lino.tutorial.part_01:

=======================
Your First Lino Project
=======================

This is a multipart tutorial for successfully doing a Lino project to publish a
blog site for beginners in Lino.

Part 01 - startproject
======================

Welcome and please be prepared to handle an extensive exposure to Lino Project.
But please do not fear the complexities, we will walk through it by examples so
that you can follow along easily. If you haven't installed the proper lino
environment, please take a look at the :doc:`/dev/install/index`, and if you did
so, we are good to go.

In this tutorial we will learn how to write a blog site.
Open up a terminal and let's get started.

Start Project
=============

Use the following command to start a new lino project::

    $ getlino startproject whitewall \
    --author="John Doe" \
    --email="johndoe@example.com" \
    --description="A personal Blog Site"

Here `startproject` is a :ref:`getlino` command :cmd:`getlino startproject` and
this creates a project named **whitewall**, which is the name we will use for
the purposes of this tutorial.

You can skip specifying the options: `--author`, `--email`, `--description` by
using another flag that we have for you, that is `--no-input`, that will let you
start a project right away. If you do not specify any of the options or flags,
you will be asked to give inputs for `Author Name`, `Author Email` and `Project
Description`. Use whichever combinations comforts you. The other variants are::

    $ getlino startproject whitewall --no-input

Creates project **whitewall** without taking the mentioned inputs.
OR::

    $ getlino startproject whitewall

You will be prompted to ask for input values. Wait until your console says Done.

Let's take a look at **whitewall** and what it contain within. The directory
structure looks like the following::

    whitewall/
        ...
        tasks.py
        tests/
            ...
        docs/
            ...
        whitewall/
            __init__.py
            setup_info.py
            lib/
                __init__.py
                whitewall/
                    __init__.py
                    settings.py
                    models.py
                    user_types.py
                    help_texts.py
                    migrate.py
                    locale/
                        ...
                users/
                    __init__.py
                    desktop.py
                    models.py
                    fixtures/
                        ...
            projects/
                __init__.py
                whitewall1/
                    __init__.py
                    manage.py
                    ...
                    tests/
                        ...
                    settings/
                        __init__.py
                        demo.py
                        ...
                        fixtures/
                            ...

Here "..." specifies directories and files that does not concern us for the
purposes of this tutorial. We are simply ignoring some files and directories
until we are prepared to talk about them. Let's try to understand this directory
tree:

    - The top **whitewall/** is the root directory for this project.
    - The :xfile:`tasks.py` file
      contains :ref:`configuration options <atelier.prjconf>`
      used by :cmd:`inv` commands.
    - Every **tests/** directory contain some test cases but does not concern us
      for this project.
    - The **docs/** directory contains documentation tree structure, also does not
      concern us for this project.
    - The next **whitewall/** directory is our primary project directory that we
      will mostly try to understand the content.
    - The **whitewall/__init__.py** is the entry to this directory for python
      **whitewall** as a package. If you are a beginner to python see: `python packages
      <https://docs.python.org/3/tutorial/modules.html#tut-packages>`_.
      All the other :file:`__init__.py` serves a similar purpose.
    - **whitewall/setup_info.py** contains meta information about our project.
      See :xfile:`setup_info.py`.
    - **whitewall/lib/** is the directory that will contain your modules/plugins.
      You will write new modules/plugins within this directory. Similar to
      django apps. If you wish to understand more about django apps,
      see: `Configuring Applications
      <https://docs.djangoproject.com/en/5.0/ref/applications/#configuring-applications>`_ in django.
    - **whitewall/lib/whitewall/** is the primary module/plugin that your projects
      will use to load into memory. More about projects in the points for paths
      in **whitewall/projects/**.
    - **whitewall/lib/whitewall/settings.py** is the file that contains your
      primary lino settings. And every other projects should inherit from here.
    - **whitewall/lib/whitewall/models.py** is the file where you can write your
      Lino models, instances of :class:`Model<lino.core.model.Model>` an extension to
      the django models. To learn more about django models see: `Model Instance Reference
      <https://docs.djangoproject.com/en/5.0/ref/models/instances/#django.db.models.Model>`_.
    - **whitewall/lib/whitewall/user_types.py** contains a :class:`ChoiceList
      <lino.core.choicelists.ChoiceList>` where you can specify and customize
      your intended user types user roles.
    - **whitewall/lib/whitewall/help_texts.py** is where lino will accumulate all
      of the help_texts you specify within your project.
    - **whitewall/lib/whitewall/migrate.py** contains your primary database migrator.
    - **whitewall/lib/whitewall/locale/** is the directory where lino will build
      your translated strings when you use multiple languages in your site.
    - **whitewall/lib/users/** is the users module for your projects that inherits
      from :mod:`users <lino.modlib.users>` module.
    - **whitewall/lib/users/desktop.py** contains the :mod:`layouts <lino.core.layouts>`
      to display user data in the frontend.
    - **whitewall/lib/users/models.py** contains your custom user model.
    - **whitewall/lib/users/fixtures/** contains demo data, that get loaded into
      database when we run :cmd:`pm prep`, and every other `fixtures` directory
      behaves the same. We will learn more about :cmd:`pm prep` later in this
      tutorial.
    - **whitewall/projects/** contains all the publishable site variants of the
      projects. Each sub-module within this directory is a publishable :class:`Site<lino.core.site.Site>`.
      Find out what you can do with a :class:`Site<lino.core.site.Site>` in :ref:`lino.tutorial.hello`.
    - `whitewall/projects/whitewall1` is your projects demo site generated by
      :cmd:`getlino startproject` command.
    - **whitewall/projects/whitewall1/manage.py** is your command line utility
      extended from django to interact with your lino project in various ways.
      See: `Django Admin and manage.py
      <https://docs.djangoproject.com/en/5.0/ref/django-admin/>`_ to learn more.
    - **whitewall/projects/whitewall1/settings/** contains the settings for this
      site, namely `whitewall1`, defined in **whitewall/projects/whitewall1/settings/demo.py**.
      This module inherits from **whitewall/lib/whitewall/settings.py**.

It's important that you understand the directory tree and are somewhat familiar
with the content of this directory tree to proceed further into Lino development.
If you feel competent please proceed to :ref:`Part 02<lino.tutorial.part_02>` of this tutorial.
