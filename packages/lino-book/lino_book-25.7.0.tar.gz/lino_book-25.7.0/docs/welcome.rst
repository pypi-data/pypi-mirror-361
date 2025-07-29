=======
Welcome
=======


.. _Debian: http://www.debian.org/

You are a :term:`software developer` and want to contribute to the :term:`Lino
framework`? That's a great idea! The world needs people like you!

.. contents::
  :local:

Audience
========

This guide is meant for people who want to contribute to Lino by writing
:term:`source code`. If you aren't a developer, you probably prefer to check out
:ref:`other ways to contribute to Lino <ss.jobs>`.

This guide assumes that you have some experience with the Python programming
language. If you are new to Python, you'll probably prefer to follow our
:doc:`Newbies Guide </dev/newbies/index>` first.

..
  This guide is meant to make sense independently of your experience level. We try
  to be understandable for newbies without being boring for veterans. We apologize
  if this goal doesn't always work out.

This guide should be useful for students, freelancers or employees,
independently of whether you work for yourself, for a :term:`development
provider` or for a :term:`site operator`.

We thought about calling this website *Programmer Guide* instead of *Developer
Guide*. Because this guide focuses on writing source code, and because
developing a software product is much more. On the other hand, especially in
`synodal software development <https://www.synodalsoft.net/how/>`__, it is
difficult to separate programming from the many other activities of the software
development business (analyse, test, write documentation, ...). We encourage
programmers to care about the whole project.

How to read this guide
======================

We recommend to read this guide sequentially. At least the first few chapters.

  "Begin at the beginning," the King said, very gravely, "and go on till you come
  to the end: then stop." -- Lewis Carroll, Alice's Adventures in Wonderland

Reading this guide sequentially means that you use the previous/next links. They
are on the top and on the bottom of each page, they are even linked to the
:kbd:`left` / :kbd:`right` arrows keys of your keyboard.

Consider the inline links in this guide like footnotes of a book: You are
welcome to follow them, but  take care to return to where you left because they
lead into a labyrinth of documentation.


Why learn Lino?
===============

Because it is :term:`sustainably free software`. You can use Lino for making
money (see :ref:`How to make money with Lino <lf.money>`). As a developer you
get our free support because helping you will help us to make Lino better, and
because we want Lino to have a sustainable and diverse community of users.

Of course we *also* hope that --once you start being successful-- you will
contribute back to Synodalsoft in a financial way. But nothing will ever force
you to do so because both source code and documentation is freely available.
Lino and its documentation, including this website, are available for free for
everybody and forever. Try to do that with some proprietary framework!

That's a big question. We are collecting answers in a separate chapter:
:doc:`/about/index`, but the short answer is: we don't know.  We actually
suggest to just read on here. Even if you find out that Lino isn't worth your
time (the worst case we can imagine), you won't have lost more time than by
watching a poor movie.

An internship at home
=====================

By following this guide you can virtually start an internship at home. If you
need help. simply `contact one of the team
<https://www.saffre-rumma.net/team/>`__ directly via email. One of us will be
your mentor and will communicate with you individually. There is no online
application form because we are a small team.  You may interrupt or abandon your
internship at any moment.

During your internship you will get quality support for free. You just need to
ask. We help you to enter the business of software development with just your
own time as your only investment. Try to do that with some proprietary
framework!

During your internship you will

- work independently and at a rhythm that suits you.
- gain experience with working in a free open-source software project
- increase your chances on the job market

You will learn among others

- how to write and maintain source code in Python, JavaScript and Sphinx
- how to use Lino and its underlying framework, Django
- how to use git for sharing your work with others
- how to monitor and use continuous integration on GitLab

Possible outcome of your internship

- Your code contributions are forever visible in the Lino repositories.
- You wrote your own :term:`Lino application`
- You set up and run a production site for a real-world :term:`site operator`
- Your mentor writes an individual internship certificate
- You find a job as a :term:`Lino application developer <application developer>`
- You start your own company as a :term:`Lino service provider <service provider>`

Of course we provide this support only as much as our human resources allow.
We do *our best*, not more.


Operating system
================

A requirement that might sound hard if you never tried it: you need to feel at
home on a Linux computer. Lino is a web application framework. A typical Lino
:term:`production site` runs on a pure Debian VPS (see
:ref:`getlino.install.prod`). Lino itself does not require a specific operating
system, but on a proprietary operating system you are likely to encounter
problems that are not our business. Welcome to the world of :ref:`Free Software
<ss.free>` :-)

In case you don't believe that this requirement is actually a chance: Seth
Kenlon shares `21 reasons why I think everyone should try Linux
<https://opensource.com/article/21/4/linux-reasons>`__. If you hesitate about
which Linux distribution to start with, we recommend Ubuntu. If you can't stop
using MS-Windows as your primary OS right now, check out Windows Subsystem for
Linux (WSL). See `here
<https://learn.microsoft.com/en-us/windows/wsl/install>`__ or  `here
<https://ubuntu.com/wsl>`__.

..
  Note that we don't force you to move to Linux. You can remain in the Windows or
  Mac world and still be useful to Lino, e.g. as a trainer, analyst or consultant,
  but in that case *you won't be a developer*. Don't waste your time reading this
  guide. We have two other guides for you, the :ref:`cg` and  :ref:`ug`.

That's why we assume that you have a computer with a Linux operating
system at your disposal.

We assume you are familiar with the Linux shell at least for basic file
operations like :cmd:`ls`, :cmd:`cp`, :cmd:`mkdir`, :cmd:`rmdir`, file
permissions, environment variables, bash scripts etc.  Otherwise we suggest to
read :ref:`Working in a UNIX shell <learning.unix>` before going on.

The developer guide is written for Debian_ and derived distributions. Other
Linuxes should be pretty similar.


Your feedback is important
==========================

Unlike Carroll's Wonderland, this guide is neither perfect nor
definitive. Lino constantly evolves. The pages on this website can become
obsolete, useless, boring, or turn out to be at the wrong place.

..
  This guide is written and maintained by volunteers.
  Lino is :term:`sustainably free software`, it belongs to us all.

So don't be shy to ask questions.
Tell your mentor when you get stuck or have the feeling that some page
is useless, boring or difficult to understand.

Keep in mind that every feedback, even critical feedback, the mere fact of
asking for help, is already a contribution to making this guide better. The
:term:`Lino community` thanks you in advance.

You don't need to be perfect, you will learn on your way, and we will help you
to learn. And which is more: *we* will learn from *you*.

..
  This is covered by the :doc:`Contributor Guide
  </contrib/index>`.
  This is documented in the :doc:`Developer Guide
  </dev/index>`.



How to contact us
=================

- Contact one of the team directly:
  https://www.saffre-rumma.net/team/

- Submit an issue to `one of our repositories on GitLab <https://gitlab.com/lino-framework>`__
  (submit to the `book repository
  <https://gitlab.com/lino-framework/book/issues>`_ if you can't
  decide which repository is the right one).

..
  Subscribe to the `developers@lino-framework.org mailing list
  <https://lists.lino-framework.org/mailman/listinfo/developers>`__
  and send an email.
