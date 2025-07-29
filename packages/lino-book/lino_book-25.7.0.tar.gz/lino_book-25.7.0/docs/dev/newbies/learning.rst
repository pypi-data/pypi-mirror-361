==================
Learning resources
==================

Here are some recommended resources for learning what you need to know as a Lino
developer. They are not specific to Lino and therefore not covered in this
guide. You don't need to read them all. We just try to help you with getting
started by providing useful pointers. Feel free to ask for guidance.

.. contents::
   :depth: 1
   :local:

.. _learning.python:

Python
======

Lino is mostly written in the Python programming language. Experienced Lino
developers know for example

- what's an object, a string, a list, a dict, a float
- the difference between a class method and an instance method
- what's a generator
- what's a decorator
- when and how to use subprocesses and threads
- what the following standard modules are being used for:
  `datetime`,  `sys`,  `os`, `re`,  `decimal`,  `logging`, `pathlib`, ...

Here are some resources for learning Python.

- Our favourite recommendation for complete beginners is the `Python tutorial at
  w3schools <https://www.w3schools.com/python/default.asp>`__

- The official `Python Tutorial <https://docs.python.org/3/tutorial/>`__

- `The Python Code Example Handbook – Simple Python Program Examples for
  Beginners
  <https://www.freecodecamp.org/news/python-code-examples-simple-python-program-example/>`__
  "This handbook will teach you Python for beginners through a series of helpful
  code examples. You'll learn basic data structures, loops, and if-then logic.
  It also includes plenty of project-oriented learning resources you can use to
  dive even deeper."

- `Everything You Need to Know (Fatos Morina)
  <https://www.freecodecamp.org/news/learn-python-book/>`__ is "my attempt to make
  it quick and easy for you to learn the essentials of Python. There are many
  other things to know about Python that I didn't cover in this book, but we
  will leave it here."

- `Sample Script Coding Tutorial for Beginners
  <https://www.freecodecamp.org/news/python-code-examples-sample-script-coding-tutorial-for-beginners/>`__
  walks you through dozens of Python
  syntax examples that all beginners should learn.
  Data structures, loops, exception handling, ...

- `Dive Into Python <https://diveintopython3.net/>`__ : Mark Pilgrim's free
  Python book for experienced programmers.

- `Think Python 2e <https://greenteapress.com/wp/think-python-2e/>`__
  : an introduction to Python programming for beginners.

- `Get into Python <https://jobtensor.com/Python-Introduction>`__, a small
  tutorial with a nice way to shortly introduce certain important concepts.
  Jobtensor is an innovative AI powered job platform for IT job seekers, so
  while you are there, you might create an account and try whether they help
  you to find a job.

- (in Estonian: `Programmeerimise õpik <https://programmeerimine.cs.ut.ee>`_)

Learning platforms:

- `Python for Beginners <https://www.codeforia.com/courses/11299948-0157-4cd8-8c87-9c5cf888abc8>`_, a tutorial in 15 lessons.

- `Django Girls Tutorial <https://tutorial.djangogirls.org/en/>`__

- `Code Academy <https://www.codecademy.com/catalog/language/python>`_

Specific topics:

- `Python 201: A Tutorial on Threads
  <https://www.blog.pythonlibrary.org/2016/07/28/python-201-a-tutorial-on-threads/>`__
  by Mike Driscoll.

- We try to follow the `Django coding style
  <https://docs.djangoproject.com/en/5.0/internals/contributing/writing-code/coding-style/>`__

- `Python Debugging With Pdb
  <https://realpython.com/python-debugging-pdb>`__ by Nathan Jennings.


Books you can buy:

- `Learn Python The Hard Way <https://learnpythonthehardway.org/>`_
  by Zed A. Shaw



.. _learning.unix:

Bash
====

- You should know the meaning of shell commands like ``ls``, ``cp``, ``rm``,
  ``cd``, ``ls``
- You can configure your local system and know about files like :xfile:`.bashrc`
  and :xfile:`.bash_aliases`.
- You know how to use shell variables and functions.
- You know what is a pipe, what is redirection
- You have written your own bash scripts.

- An in-depth exploration of the art of shell scripting: `Advanced
  Bash-Scripting Guide <https://www.tldp.org/LDP/abs/html>`_ by Mendel
  Cooper

- Bash Cheat sheets: `learncodethehardway.org
  <https://learncodethehardway.org/unix/bash_cheat_sheet.pdf>`__,
  `pcwdld.com <https://www.pcwdld.com/bash-cheat-sheet>`__

- `Bash guide on Greg's wiki <http://mywiki.wooledge.org/BashGuide>`_

- `Steve Parker's shell scripting guide
  <http://steve-parker.org/sh/first.shtml>`_

- `BASH Programming - Introduction HOW-TO
  <http://tldp.org/HOWTO/Bash-Prog-Intro-HOWTO.html>`_ by Mike G

- http://books.goalkicker.com/BashBook/



Django
======

Lino applications are Django projects. Before you start to learn Lino, it makes
sense to follow the `Django Tutorial
<https://docs.djangoproject.com/en/5.0/>`__.

- Django's ORM layer : the `Model
  <https://docs.djangoproject.com/en/5.0/topics/db/models/>`__ class, the `field
  types
  <https://docs.djangoproject.com/en/5.0/topics/db/models/#field-types>`__,
  making `database queries <https://docs.djangoproject.com/en/5.0/topics/db/queries/>`__, ...

- What a :xfile:`settings.py` file is and how to get a Django project up and
  running.


Sphinx
======

Documentation about Lino is written using `Sphinx <https://sphinx-doc.org>`_.

- `Tutorial <https://sphinx-doc.org/tutorial.html>`__

- You should know how Sphinx works and why we use it to write Lino
  documentation.  See :doc:`/dev/builddocs` for the first steps.

- Maybe one day you will want to have your own :doc:`developer blog
  </dev/devblog>` for writing about your contributions to Lino.


SQL
===

- `SQL Tutorial <https://www.w3schools.com/sql/>`_
- `Udemy's Beginner’s Guide to SQL
  <https://blog.udemy.com/beginners-guide-to-sql/>`__


Git
===

Lino is hosted on GitHub and GitLab (see also :doc:`/team/gh2gl`).
You need to know how to use these collaboration platforms.

- Read the `GitHub Help <https://help.github.com>`_ pages,
  especially the "Bootcamp" and "Setup" sections.
- `Atlassian's Git Tutorial <https://www.atlassian.com/git/tutorials>`__
- `GitHub Help site <https://help.github.com/>`__
- `Udemy Comprehensive Git Guide
  <https://blog.udemy.com/git-tutorial-a-comprehensive-guide/>`__
- `GitKraken <https://www.gitkraken.com>`__ can help to understand things.

Try out what you've learned:

- Create a free account on GitLab and made a fork of Lino.
- Try to make some change in your working copy, commit your
  branch and send a pull request.
- See also :doc:`/dev/git` and :doc:`/dev/request_pull`.

HTML, CSS and JavaScript
========================

- You need to understand the meaning of tags like
  ``<body>``, ``<ul>``, ``<li>`` ...
- You should know what an AJAX request is.

- `FreeCodeCamp <https://www.freecodecamp.org>`__
- `HTML Tutorial <http://www.w3schools.com/html/>`_
- `CSS Tutorial <http://www.w3schools.com/css/>`_
- `JavaScript Tutorial <http://www.w3schools.com/js/>`_



Databases
=========

Lino is a part of Django and therefore uses relational databases (SQL). You
don't usually need to write SQL yourself when using Lino, but it is of course
important to understand the concepts behind a database. And on a production
server you will have to deal with database servers like MySQL or PostgreSQL
when doing database snapshots or running migrations.



Software development in general
===============================

Quincy Larson's book `How to Learn to Code & Get a Developer Job in 2023
<https://www.freecodecamp.org/news/learn-to-code-book/>`__ is freely available
to anyone who wants to learn to code and become a professional developer. "This
book will teach you insights I've learned over the past decade: from my own
journey into coding as a teacher in my 30s, from working as a software engineer,
and from running freeCodeCamp.org. If you're looking for a good starting point
for your developer journey, this book is for you. You can read the whole thing
now."
