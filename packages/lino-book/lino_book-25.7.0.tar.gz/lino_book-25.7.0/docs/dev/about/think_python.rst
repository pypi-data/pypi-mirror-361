.. _lino.think_python:

============
Think Python
============

Lino is a tool for experienced professional Python developers. We believe that
database structure, screen layouts and business logic should be written *in
plain Python* rather than in some additional text file format like XML, or using
a visual GUI editor.

The advantages are better maintainability, better re-usability, less complexity.

Yes, this requires you to know Python before you can see a result.

This choice is important when it comes to maintaining complex database
applications in a sustainable way.

Rob Galanakis explains a similar opinion in `GeoCities and the Qt Designer
<https://www.robg3d.com/2014/08/geocities-and-the-qt-designer/>`_: "We’ve had
WYSIWYG editors for the web for about two decades (or longer?), yet I’ve never
run into a professional who works that way. I think WYSIWYG editors are great
for people new to GUI programming or a GUI framework, or for mock-ups, but it’s
much more effective to do production GUI work through code. Likewise, we’ve had
visual programming systems for even longer, but we’ve not seen one that produces
a result anyone would consider maintainable."

For example, one of Lino's powerful features are :ref:`layouts <layouts>` whose
purpose is to describe an input form programmatically in the Python language.
Compare the :class:`UserDetail` classes defined in :class:`lino.modlib.users`
and :class:`lino_noi.lib.users`.

Imagine a customer 1 who asks you to write an application 1. Then a second
customer asks you to write a similar application, but with a few changes. You
create application 2, using application 1 as template. One year later customer 1
asks for an upgrade. And during that year you have been working on application
2. You will have added new features, fixed bugs, written optimizations... some
of these changes are interesting for customer 1, and they will be grateful if
they get them for free, without having asked for them. Some other changes may
*not* be welcome to your customer 1.

Thinking in Python is optimal when you are working for a software house with
more than a few customers using different variants of some application for which
you offer long-term maintenance.

Python is a powerful and well-known parser, why should we throw away a subset of
its features by introducing yet another description language?

Or another example: Lino has no package manager because we have pip and git. We
don't need to reinvent them.

Why do other frameworks reinvent these wheels?  Because it enables them to have
non-programmers do the database design, screen layout and deployment.  Which is
a pseudo-advantage.  Lino exists because we believe that database design, screen
layout and deployment should be done to people who *think in Python*.

This does not exclude usage of templates when meaningful, nor features like
user-defined views because end-users of course sometimes want to save a given
grid layout.
