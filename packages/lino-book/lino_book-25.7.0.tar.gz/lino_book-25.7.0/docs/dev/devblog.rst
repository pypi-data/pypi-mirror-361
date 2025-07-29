.. _devblog:

=============================
Start your own developer blog
=============================

This section explains what a :term:`developer blog` is, why you need it, why
*we* need it, and how you do it.

.. glossary::

  developer blog

    A blog written by a developer about his work.


Why you want to blog
====================

The basic idea of a developer blog is that you leave a trace about what you have
been doing, and that this trace is accessible at least to yourself. Its primary
goal is not to gain attention.

In your developer blog you report about your daily work.  Day by day. Using
plain English language. It is your diary.

My first developer blog was a simple plain text file (one per month) where I
noted every code change for my own reference.  It happens surprisingly often
that I want to know why I did some change one year ago.  And I was often amazed
about how many things both my customers and I were able to forget during one
year.

A public developer blog can be the easiest way to ask for help in complex cases
that need screenshots, links, sections etc.

2021-03-26 Mario Jason Braganza shares his `Thoughts on Setting Up a Blog
<https://janusworx.com/blog/thoughts-on-setting-up-a-blog/>`__.

2024-05-24 Max Pekarsky writes `You should keep a developer’s journal
<https://stackoverflow.blog/2024/05/22/you-should-keep-a-developer-s-journal/>`__




Why *we* want you to blog
=========================

When you develop or maintain a software used by people who pay you for this job,
explaining *what you change* and *why you change it* is more important than
actually fixing their problem.

Of course it's not always easy to explain what you are doing.  The daily work of
a software developer includes things like modifying source code, pushing changes
to public repositories, writing comments in forums, surfing around, reading
books, discovering new technologies, dreaming about a better world, reinventing
wheels...

What kind of blog you need as a developer
=========================================

Write your developer blog using your editor of choice.    It is a waste of
energy to constantly switch back and forth between different editors depending
on whether you write *code* or *about* your code

Use a static html generator because that gives you the power of Git for version
control.

A developer blog usually has at most one entry per day, each entry having
potentially a series of headings. That's because you often cannot know in
advance what is going to happen during your day.


Qualities of a developer blog
=============================

A developer blog does not need to be **cool**, **exciting**, **popular** or **easy
to follow**.  It should rather be:

- **complete** (e.g. don't forget to mention any relevant code change
  you did)

- **concise** (e.g. avoid re-explaining things that are explained somewhere
  else)

- **understandable** (e.g. use references to point to these other places so that
  a reader with enough time and motivation has a chance to follow).

Note that these qualities are listed in order of difficulty.  Being *complete*
is rather easy and just a question of motivation.  Staying *concise* without
becoming incomplete takes some exercise.  And being *understandable* requires
some talent and much feedback from readers.  In practice it's already a good
thing when you manage to be understandable at least to yourself.

Note also that none of these qualities is required.  Even an incomplete and
unconcise developer blog is better than no blog at all.


Going public
============

When working as a professional on a free software project, it is important that
you share your developer blog in a public place where others can access it.
Your blog becomes an integral part of the software.  You share your know-how,
your experience and your learning (which includes successes, failures and
stumblings).  You share it also with future contributors who might want to
explore why you have been doing things the way you did them.

Before publishing your blog, make sure that you understand the usual rules:

- Don't disclose any passwords or confidential data.
- Respect other people's privacy.
- Reference your sources of information.
- Don't quote other author's words without naming them.



Luc's blogging system
=====================

You probably know already one example of a public developer blog,
namely `Luc's developer blog <https://luc.lino-framework.org>`_.  The
remaining sections describe how you can use Luc's system for your own
blog.

You may of course use another blogging system (blogger.com,
wordpress.com etc,), especially if you have been blogging before.

Luc's developer blog is free, simple and extensible.
It answers well to certain requirements that we perceive as
important:

- A developer uses some editor for writing code, and wants to use that
  same editor for writing his blog.

- A developer usually works on more than one software projects at a
  time.

- A developer should not be locked just because there is no internet
  connection available for a few hours.

It is based on `Sphinx <http://sphinx-doc.org/>`_, which is the
established standard for Python projects. This has the advantage that
your blog has the same syntax as your docstrings.

Followers can subscribe to it using an RSS reader.


"Blog" versus "Documentation tree"
==================================

Luc's blogging system uses *daily* entries (maximum one blog entry per
day), and is part of some Sphinx documentation tree.

But don't mix up "a blog" with "a documentation tree".  You will
probably maintain only one *developer blog*, but you will maintain
many different *documentation trees*.  Not every documentation tree
contains a blog.

You probably will soon have other documentation trees than the one
which contains your blog. For example your first Lino application
might have a local project name "hello", and it might have two
documentation trees, one in English (`hello/docs`) and another in
Spanish (`hello/docs_es`). :cmd:`inv pd` would upload them to
`public_html/hello_docs` and `public_html/hello_docs_es` respectively.
See :attr:`env.docs_rsync_dest <atelier.fablib.env.docs_rsync_dest>`.


.. _dblog:

The `dblog` project template
============================

To help you get started with blogging in your own developer blog,
there is a project template at https://github.com/lsaffre/dblog


.. You may find inspiration from the Lino website for configuring your
   developer blog.

    - Interesting files are:
      :file:`/docs/conf.py`
      :file:`/docs/.templates/layout.html`
      :file:`/docs/.templates/links.html`
