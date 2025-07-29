.. doctest docs/dev/plugins.rst
.. _dev.plugins:

=======================
More about plugins
=======================

.. currentmodule:: lino.core.plugin

A **plugin** is a Python module that encapsulates a set of *functionality*
designed to be used in more than one application. It can define database models,
actors, actions, fixtures, template files, JavaScript snippets, dependencies,
and :term:`configuration settings <plugin configuration setting>`.  None of
these are mandatory.

See :doc:`/plugins/index` for a list of the plugins defined in Lino and the XL.

A **plugin** in Lino corresponds to what *Django* calls an "application". See
also :doc:`application`.

.. contents::
  :local:


Usage overview
==============


The :term:`application developer` defines which plugins to install in the
application's :meth:`get_installed_plugins
<lino.core.site.Site.get_installed_plugins>` method.

The plugin developer defines a plugin in the :xfile:`__init__.py` file of the
package.  Lino expects this file to define a class named ``Plugin``, which
inherits from the abstract base :class:`Plugin <lino.core.plugin.Plugin>` class.
Your :class:`Plugin <lino.core.plugin.Plugin>` class is the central description
of your plugin.

Here is a fictive example::

    from lino.api import ad, _

    class Plugin(ad.Plugin):
        verbose_name = _("Better calendar")
        extends = 'mylib.cal'
        needs_plugins  = ['lino_xl.lib.contacts']

        def setup_main_menu(self, site, user_type, m):
            m = m.add_menu(self.app_label, self.verbose_name)
            m.add_action('cal.Teams')
            m.add_action('cal.Agendas')


A plugin can **depend on other plugins** by specifying them in the
:attr:`needs_plugins <lino.core.plugin.Plugin.needs_plugins>`
attribute. This means that when you install this plugin, Lino will
automatically install these other plugins as well

A plugin can define a set of **menu commands** using methods like
:meth:`setup_main_menu
<lino.core.plugin.Plugin.setup_main_menu>`. This is explained in
:doc:`menu`.

A plugin can **extend** another plugin by inheriting from its :class:`Plugin`
class. This is explained in :doc:`plugin_inheritance`.

A plugin that extends another plugin can optionally extend one or multiple
database models defined by the parent plugin. If it does so, it must declare
their names in :attr:`extends_models
<lino.core.plugin.Plugin.extends_models>`.


.. _dev.accessing.plugins:


Accessing plugins
=================

Django developers are used to code like this::

    from myapp.models import Foo

    def print_foo(pk=1):
        print(Foo.objects.get(pk=pk))

In Lino we prefer to use the :attr:`rt.models <lino.api.rt.models>` dict as
follows::

    from lino.api import rt

    def print_foo(pk=1):
        Foo = rt.models.myapp.Foo
        print(Foo.objects.get(pk=pk))

This approach has the advantage of providing :doc:`plugin_inheritance`. One of
the basic reasons for using plugins is that another developer can extend it and
use their extension instead of the original plugin. Which means that the plugin
developer does not know (and does not *want* to know) where the model classes
are actually defined.

Note that :attr:`rt.models <lino.api.rt.models>` is populated only
*after* having imported the models. So you cannot use it at the
module-level namespace of a :xfile:`models.py` module.  For example
the following variant of above code **would not work**::

    from lino.api import rt
    Foo = rt.models.foos.Foo  # error `AttrDict has no item "foos"`
    def print_foo(pk=1):
        print(Foo.objects.get(pk=pk))

Plugin descriptors get defined and configured before Django models start to
load.  Lino creates one :class:`Plugin` instance for every installed plugin and
makes it globally available in :attr:`dd.plugins.FOO
<lino.core.site.Site.plugins>` (where `FOO` is the :attr:`app_label
<Plugin.app_label>` of the plugin).

The :class:`Plugin` class is comparable to Django's `AppConfig
<https://docs.djangoproject.com/en/5.0/ref/applications/>`_ class,
which has been added in version 1.7., but there is at least one
important difference: in Lino the :class:`Plugin` instances for
all installed plugins are available (in :attr:`dd.plugins
<lino.core.site.Site.plugins>`) *before* Django starts to load the
first :xfile:`models.py`.  This is possible because Plugins are
defined in :xfile:`__init__.py` files of your plugins. As a
consequence, unlike Django's `AppConfig`, you *cannot* define a
`Plugin` in your :xfile:`models.py` file, you *must* define it in
your plugins's :xfile:`__init__.py`.



Configuring plugins
===================

.. currentmodule:: lino.core.site

Plugins can have **attributes** for holding configuration settings that
are not
meant to configured by site users via the web interface.

For example, the :setting:`countries.country_code` setting is defined as
follows::

  ...
  class Plugin(ad.Plugin):
      ...
      country_code = 'BE'


The values of plugin attributes can be configured at three levels.

As a :term:`core developer` you specify a hard-coded default value.

As an :term:`application developer` you can specify default values in your
application by overriding the :meth:`Site.get_plugin_configs` of your Site
class.  For example::

    class Site(Site):

        def get_plugin_configs(self):
            yield super().get_plugin_configs()
            yield 'countries', 'country_code', 'FR'
            yield 'contacts', 'hide_region', True


As a :term:`server administrator` you can override these configuration
defaults in your project's :xfile:`settings.py`


.. currentmodule:: lino.core.site

The :meth:`Site.get_plugin_setting` method
==========================================

Some use cases for testing the :meth:`Site.get_plugin_setting` method:

>>> from lino import startup
>>> startup('lino_book.projects.min1.settings')
>>> from lino.api.doctest import *

>>> settings.SITE.get_plugin_setting('foo', 'bar')
Traceback (most recent call last):
...
Exception: Plugin foo is not installed and no default was provided

>>> settings.SITE.get_plugin_setting('contacts', 'bar')
Traceback (most recent call last):
...
AttributeError: 'Plugin' object has no attribute 'bar'

In both cases, you can avoid the traceback by specifying a default value:

>>> print(settings.SITE.get_plugin_setting('foo', 'bar', None))
None

>>> settings.SITE.get_plugin_setting('contacts', 'bar', 'baz')
'baz'




The old style using :meth:`Site.setup_plugins` still works but is deprecated::

    class Site(Site):

        def setup_plugins(self):
            super().setup_plugins()
            self.plugins.countries.configure(country_code='BE')
            self.plugins.contacts.configure(hide_region=True)

Note that :meth:`Site.setup_plugins` is called *after*
:meth:`Site.get_plugin_configs`. This can cause unexpected behaviour when you
mix both methods.


using one of the
following methods:

- by overriding the Site class as described above for application
  developers

- by setting the value directly after instantiation of your
  :setting:`SITE` object.


.. glossary::

  plugin configuration setting

    A setting that can easily be set in a :xfile:`settings.py` file.
