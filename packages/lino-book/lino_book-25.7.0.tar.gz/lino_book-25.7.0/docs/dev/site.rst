.. doctest docs/dev/site.rst
.. _dev.site:

=======================================
Introduction to the :class:`Site` class
=======================================

.. contents::
    :depth: 1
    :local:


.. currentmodule:: lino.core.site

A Lino application is defined by its :class:`Site` class
========================================================

A Django project becomes a :term:`Lino site` when a :term:`Django settings
module` has a variable named :setting:`SITE` holding an instance of a subclass
of the :class:`lino.core.site.Site` class.

The :class:`lino.core.site.Site` class is the ancestor of all Lino applications.
It is designed to be subclassed by the :term:`application developer`, then
imported into a local :xfile:`settings.py`, where a :term:`server administrator` may
possibly subclass it another time.

Subclassing the :class:`Site` class doesn't yet make a Lino site: a Lino site
starts to exist when such a :class:`Site` class gets *instantiated* in a
:term:`Django settings module`.  Lino does quite a few things during this
instantiation.

This concept brings an additional level of encapsulation to Django. Django
settings usually contain simple values (strings, integers, or lists or
dictionaries thereof).  But Lino's :setting:`SITE` setting holds a *Python
object*, with methods that can be called by application code at runtime.

To hook this into Django, imagine the :class:`Site` *class* as a kind of a
"project model". Read :doc:`application` if you wonder why we chose that name.

In other words, the central and fundamental definition of a :term:`Lino
application` is formulated by a :class:`Site` class object. This :class:`Site`
class object is *not* defined in a :term:`Django settings module` but as part of
the Python package that implements your application.

Remember the :doc:`/discover`

For example, the :class:`Site` class for :ref:`noi` is defined in the module
:mod:`lino_noi.lib.noi.settings`.  Please have a look at its `source code
<https://gitlab.com/lino-framework/noi/-/blob/master/lino_noi/lib/noi/settings.py>`__.

..
  :mod:`lino_voga.lib.voga.settings`.  Please have a look at its `source code
  <https://gitlab.com/lino-framework/voga/-/blob/master/lino_voga/lib/voga/settings.py>`__.

Note that this module *defines* a :class:`Site` class object but does *not
instantiate* it.  You can import this module into a :term:`Django settings
module`, but you cannot use it directly as a settings module.  The following
attempt can only fail:

>>> from lino import startup
>>> startup('lino_voga.lib.voga.settings')
>>> from lino.api.rt import *
Traceback (most recent call last):
...
AttributeError: 'Settings' object has no attribute 'SITE'

Example of a Lino site that uses the Voga application is in the :doc:`voga3
</projects/voga3>` demo project, which has its :xfile:`settings.py` file in the
:mod:`lino_book.projects.voga3.settings` module of the book repository.
Please have also a look at this `source code
<https://gitlab.com/lino-framework/book/-/blob/master/lino_book/projects/voga3/settings.py>`__

You can see that this :xfile:`settings.py`

- imports everything from :mod:`lino_voga.lib.voga.settings`,
- subclasses the site by saying ``class Site(Site):``
- instantiates the site by saying ``SITE = Site(globals())``

That's why you can use it as a :term:`Django settings module`.


Often-used attributes of :class:`Site`
======================================

In your :class:`Site` class you define some general description of your
application.

.. setting:: title

    The title to appear in the browser window.  If this is None, Lino will use
    :setting:`verbose_name` as default value.

.. setting:: verbose_name

    The name of this application, to be displayed to end users at different
    places.

Note the difference between :setting:`title` and :setting:`verbose_name`:

- :setting:`title` may be None, :setting:`verbose_name` not.

- :setting:`title` is used by the
  :srcref:`index.html <lino/modlib/extjs/config/extjs/index.html>` for
  :mod:`lino.modlib.extjs`.

- :setting:`title` and :setting:`verbose_name` are used by
  :xfile:`admin_main.html` to generate the fragments "Welcome to the
  **title** site" and "We are running **verbose_name** version
  **x.y**"  (the latter only if :attr:`version` is set).

- :meth:`Site.site_version` uses :setting:`verbose_name` (not :setting:`title`)

IOW, the :setting:`title` is rather for usage by a :term:`server administrator`,
while the :setting:`verbose_name` is rather for usage by the :term:`application
developer`.

.. setting:: version

  An optional version number.

  Common practice is to fill this from your SETUP_INFO.

.. setting:: url

  The URL of the website that describes this application.

  Used e.g. in a :menuselection:`Site --> About` dialog box.

  Common practice is to fill this from your SETUP_INFO.


See also
:meth:`Site.site_version`
:meth:`Site.welcome_text`
:meth:`Site.using_text`


.. _dg.site.get_installed_plugins:

How Lino builds the INSTALLED_APPS setting
==========================================

In a Lino application you set your :setting:`INSTALLED_APPS` indirectly by
overriding the :meth:`get_installed_plugins <Site.get_installed_plugins>`
method. Alternatively, in very small projects (such as the projects in
:doc:`/tutorials/index`) you might prefer to specify them as positional
arguments to the :class:`Site <lino.core.site.Site>` constructor.

Example (taken from :doc:`chatter </projects/chatter>`)::

  def get_installed_plugins(self):
      yield 'lino.modlib.users'
      yield 'lino_xl.lib.groups'
      yield 'lino.modlib.comments'
      yield 'lino.modlib.notify'
      yield super().get_installed_plugins()

Lino calls this method exactly once at :term:`site startup`, and it expects it
to yield a list of strings. More precisely, each yield item must be *either* a
Python module name *or* a generator to be iterated recursively (again expecting
either strings or generators of strings).

The resulting list of names will then possibly altered by the
:meth:`get_plugin_modifiers` method.

Lino then stores the resulting list into the :setting:`INSTALLED_APPS` setting.

When you override the :meth:`Site.get_installed_plugins` method, don't forget to
call the :func:`super` method. This is important because the core
:meth:`get_installed_plugins <Site.get_installed_plugins>` method yields a
series of plugins: :mod:`lino.modlib.about`, :mod:`lino.modlib.ipdict`, the
:attr:`web_front_ends <lino.core.site.Site.web_front_ends>`, and maybe even more
(as an application developer you don't want to worry about these technical
details).

You should call the :func:`super` method at the end (not at the beginning) of
your own method because the ordering of installed plugins has an influence on
the :term:`application menu` and you probably want the plugins returned by the
super method to come at the end of the menu because they are rather "technical"
compared to your rather "application-specific" menu items.

Additional local plugins
========================

An optional second positional argument can be specified by the  :term:`server
administrator` in order to specify additional *local plugins*. These will go
into the :setting:`INSTALLED_APPS` setting, together with any other plugins
needed by them. As an :term:`application developer` you won't specify this
argument, you should specify your installed plugins by overriding
:meth:`get_installed_plugins <Site.get_installed_plugins>`.

>>> from lino_book.projects.min1.settings import Site
>>> pseudoglobals = {}
>>> Site(pseudoglobals, "lino_xl.lib.events")  #doctest: +ELLIPSIS
<lino_book.projects.min1.settings.Site object at ...>
>>> print('\n'.join(pseudoglobals['INSTALLED_APPS']))
... #doctest: +REPORT_UDIFF +NORMALIZE_WHITESPACE
lino
lino.modlib.about
lino.modlib.jinja
lino.modlib.bootstrap3
lino.modlib.extjs
lino.modlib.printing
lino.modlib.system
lino.modlib.users
lino.modlib.office
lino_xl.lib.xl
lino_xl.lib.countries
lino_xl.lib.contacts
django.contrib.staticfiles
lino_xl.lib.events
django.contrib.sessions


.. class:: Site
  :noindex:

  .. method:: get_installed_plugins(self)

      Yield the list of plugins to be installed on this site.

      See :ref:`dg.site.get_installed_plugins`.

  .. method:: get_plugin_configs(self)

      Return a series of plugin configuration settings.

      This is called before plugins are loaded.  :attr:`rt.plugins` is not
      yet populated.

      The method must return an iterator that yields tuples with three items
      each: The name of the plugin, the name of the setting and the
      value to set.

      Example::

        def get_plugin_configs(self):
            yield super().get_plugin_configs()
            yield ('countries', 'hide_region', True)
            yield ('countries', 'country_code', 'BE')
            yield ('vat', 'declaration_plugin', 'lino_xl.lib.bevats')
            yield ('accounting', 'use_pcmn', True)
            yield ('accounting', 'start_year', 2014)


  .. method:: get_plugin_modifiers(self, **kwargs)

      Override or hide individual plugins of the application.

      Deprecated because this approach increases complexity instead of
      simplifying things.

      For example, if your site inherits from
      :mod:`lino.projects.min2`::

        def get_plugin_modifiers(self, **kw):
            kw = super().get_plugin_modifiers(**kw)
            kw.update(sales=None)
            kw.update(courses='my.modlib.courses')
            return kw

      The default implementation returns an empty dict.

      This method adds an additional level of customization because
      it lets you remove or replace individual plugins from
      :setting:`INSTALLED_APPS` without rewriting your own
      :meth:`get_installed_plugins`.

      This will be called during Site instantiation and is expected to
      return a dict of `app_label` to `full_python_path`
      mappings which you want to override in the list of plugins
      returned by :meth:`get_installed_plugins`.

      Mapping an `app_label` to `None` will remove that plugin from
      :setting:`INSTALLED_APPS`.

      It is theoretically possible but not recommended to replace an
      existing ``app_label`` by a plugin with a different
      ``app_label``. For example, the following might work but is not
      recommended::

         kw.update(courses='my.modlib.myactivities')
