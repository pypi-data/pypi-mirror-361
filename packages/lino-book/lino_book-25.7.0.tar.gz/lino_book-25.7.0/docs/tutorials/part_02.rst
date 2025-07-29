.. _lino.tutorial.part_02:

=======================
Your First Lino Project
=======================

This document is a continuation of the multipart tutorial for doing a Lino
project to publish a blog site. If you did not go through the :ref:`Part
01<lino.tutorial.part_01>` of this tutorial please do so before proceeding with
this document, unless of course you feel competent enough to follow.

Part 02 - Setting up locale and installing the project into python path
=======================================================================

In this part of the tutorial we will modify some the files within our project
that we got acquainted with in the previous part of the tutorial. We will setup
languages, timezones and after, we will install our project into python
environment.

Setting up languages
--------------------

Our **whitewall** project is now configured to provide support for english(en),
deutsch(de) - German and french(fr) but for the purposes of this tutorial we
will use only english(en) as our project language.

The file **tasks.py** our root directory currently look like the following::

    from atelier.invlib import setup_from_tasks
    ns = setup_from_tasks(
        globals(), "whitewall",
        languages="en de fr".split(),
        # tolerate_sphinx_warnings=True,
        locale_dir='whitewall/lib/whitewall/locale',
        revision_control_system='git',
        cleanable_files=['docs/api/whitewall.*'],
        demo_projects=['whitewall.projects.whitewall1'])

We will replace the value for keyword argument for languages in
:meth:`setup_from_tasks`, which currently taking **"en de fr".split()**, with
**['en']**, saying we want english(en) as our only language. After this change,
the code should look like the following::

    from atelier.invlib import setup_from_tasks
    ns = setup_from_tasks(
        globals(), "whitewall",
        languages=['en'],
        # tolerate_sphinx_warnings=True,
        locale_dir='whitewall/lib/whitewall/locale',
        revision_control_system='git',
        cleanable_files=['docs/api/whitewall.*'],
        demo_projects=['whitewall.projects.whitewall1'])

Similarly, the last few lines of code of the file **whitewall/setup_info.py**
look like the following::

    for lng in 'de fr'.split():
        l.append('locale/%s/LC_MESSAGES/*.mo' % lng)

We will simply remove this for loop since we are not using any other languages
than english(en) and do not require any translation capability. And after doing
so this **whitewall/setup_info.py** file should end on the following line of
code::

    l = add_package_data('whitewall.lib.whitewall')

And lastly for language, we will have to do another modification on the
**whitewall/projects/whitewall1/settings.demo.py** file, where the first few
lines of the class object :class:`Site<lino.core.site.Site>` looks like the following::

    class Site(Site):

        is_demo_site = True
        the_demo_date = datetime.date(2015, 5, 23)

        languages = "en de fr"

Here we will also replace the value for the :attr:`languages` with **"en"**, so,
the object now should look like the following::

    class Site(Site):

        is_demo_site = True
        the_demo_date = datetime.date(2015, 5, 23)

        languages = "en"

Here we are done for changes in the site language. Let's now take a look at
where we can change the site's timezone information.

Setting up timezone
-------------------

At the end of the **whitewall/projects/whitewall1/settings.demo.py** file, we
have::

    USE_TZ = True
    TIME_ZONE = 'UTC'

This explicitly says we want to use timezone info and we want our current
timezone to be 'UTC' so we left it as it is. It's what we want for the purposes
of this tutorial.

Installing our project
----------------------

To install the our project `cd` (unix command) into our root directly, name inside our top
level **whitewall/** directory. And run the following command::

    $ python -m pip install -e .

This will install our project into python environment in editing mode so that
any changes we do in our project will be reflected in python immediately.

It's important that you understand the the changes we did in this part of the
tutorial to proceed further into Lino development. If you feel competent please
proceed to :ref:`Part 03<lino.tutorial.part_03>` of this tutorial.
