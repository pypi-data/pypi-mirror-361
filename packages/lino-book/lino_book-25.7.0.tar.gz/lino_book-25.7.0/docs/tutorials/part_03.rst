.. _lino.tutorial.part_03:

=======================
Your First Lino Project
=======================

This document is a continuation of the multipart tutorial for doing a Lino
project to publish a blog site. If you did not go through :ref:`Part
02<lino.tutorial.part_02>` of this tutorial please do so before proceeding with
this document, unless of course you feel competent enough to follow.

Part 03 - Installing :mod:`blogs<lino_xl.lib.blogs>` plugin and running a server
================================================================================

In this part of the tutorial we will install the :mod:`blogs<lino_xl.lib.blogs>`
plugin in our project that lino provides for us and run a local server to see
our work this far in action.

Installing :mod:`blogs<lino_xl.lib.blogs>` plugin
-------------------------------------------------

We will modify **whitewall/lib/whitewall/settings.py** file, remember every
other projects or sites inherits from this file, any changes we do in this file
will be reflected on every other site that we have in our project.

Let's take a first look at some of the content of this file::

    class Site(Site):
        ...
        def get_installed_plugins(self):
            """Implements :meth:`lino.core.site.Site.get_installed_plugins`.

            """
            yield super(Site, self).get_installed_plugins()
            yield 'whitewall.lib.users'
            yield 'whitewall.lib.whitewall'

Here, as always, the three dots "..." implies and will imply that there are some
code there which we ignore because they do not concern us for the moment. To try
to understand the method :meth:`get_installed_plugins` by looking at this code we
can conclude that it's calling super, ``yield super(Site,
self).get_installed_plugins()`` so that Lino's internal dependencies plugins are
loaded properly and after calling super it's installing two more plugins here::

    yield 'whitewall.lib.users'
    yield 'whitewall.lib.whitewall'

The users and whitewall plugin that we have within our project. If we write more
plugins with more capabilities we will also have to pass them through this
method so that they are loaded into our site.

To install the :mod:`blogs<lino_xl.lib.blogs>` plugin in our project we only
have to add this line of code ``yield 'lino_xl.lib.blogs'`` to this method. And
after doing so our :class:`Site<lino.core.site.Site>` object now look like the following::

    class Site(Site):
        ...
        def get_installed_plugins(self):
            """Implements :meth:`lino.core.site.Site.get_installed_plugins`.

            """
            yield super(Site, self).get_installed_plugins()
            yield 'whitewall.lib.users'
            yield 'whitewall.lib.whitewall'
            yield 'lino_xl.lib.blogs'

We now have blog functionalities within our project. Let's try to run a a site
on local machine and see how our site looks like.

Running a server
----------------

We can have multiple sites within our **whitewall/projects/** directory but at
the moment we only have **whitewall1** as our only site. Before running the
server we need to populate our database with the model schemas and to do that
let's `cd` into the **whitewall/projects/whitewall1** directory and run the
following command::

    $ pm prep

Your will be prompted to ask for confirmation. Press RETURN key to confirm and
lino will take y (for yes) as the default value. This will populate our
database.

Now, do the following command::

    $ runserver

And this will run a local server and you will see some information about our
server in your console, the last bit of which should look like this::

    Django version 3.2.5, using settings 'whitewall.projects.whitewall1.settings.demo'
    Starting development server at http://127.0.0.1:8000/
    Quit the server with CONTROL-C.

Your django version may vary but otherwise everything should be the same. Here,
`http://127.0.0.1:8000/` is the address:port to which our server is listening
for requests. Open up your favorite browser and visit the link: `http://127.0.0.1:8000/`.
