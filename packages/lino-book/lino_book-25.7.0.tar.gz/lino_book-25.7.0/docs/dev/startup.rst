.. _startup:

===================
When Lino starts up
===================

.. currentmodule:: lino.core.site

Here is what happens when a :term:`Lino process` wakes up.

.. contents::
    :depth: 1
    :local:


The life cycle of a Lino process
================================

.. glossary::

  site startup

    The things that happen at the beginning of a :term:`Lino process`.

  Lino process

    A Python process running on a given :term:`Lino site`.  This is either some
    :term:`django-admin command`, or a WSGI or ASGI process inside a web server.

There are **four major phases** in the life of a :term:`Lino process`:

.. glossary::

  application definition

    The first phase of the :term:`site startup` when Django **settings** are
    being loaded. We see this as a separate phase because Lino does some magics
    there.

  data definition

    The second phase of the :term:`site startup`, when Django  loads the
    **database models** and does its own startup.

  site analysis

    The third phase of the :term:`site startup`, when Django models have been
    loaded, and Lino analyses them to fill its own data structures.

  runtime

    When the :term:`site startup` has finished and the actual process does what
    it is designed to do.

There are **three modules** in :mod:`lino.api` named after these phases:

- :mod:`lino.api.ad` is available during :term:`application definition`.

- :mod:`lino.api.dd` is available during :term:`data definition` and
  :term:`site analysis`.

- :mod:`lino.api.rt` is available when :term:`site analysis` has finised.


Application definition
======================

The :term:`application definition` phase:

(:count:`step`) :xfile:`manage.py` sets :envvar:`DJANGO_SETTINGS_MODULE` and
calls :func:`django.core.management.execute_from_command_line`, which loads your
:xfile:`settings.py` file.

(:count:`step`) Importing the :xfile:`settings.py` module will instantiate your
:setting:`SITE`. Here is what happens when the :class:`Site` class gets
*instantiated*.

(:count:`step`) Modify Django's :data:`django.utils.log.DEFAULT_LOGGING` dict.

(:count:`step`) Call :meth:`Site.get_plugin_configs`

(:count:`step`) Read the :xfile:`lino.ini` if it exists.

(:count:`step`) Call :meth:`Site.get_plugin_modifiers` and
:meth:`Site.get_installed_plugins` to build the list of plugins.

(:count:`step`) Import each plugin (just the :file:`__init__.py` of the
package).

(:count:`step`) Set the :setting:`INSTALLED_APPS` setting and the
:attr:`Site.installed_plugins` site attribute. The list of installed plugins is
now known and won't change any more. :setting:`INSTALLED_APPS` is basically the
same as :attr:`Site.installed_plugins`, except that the former is a list of
module names while the latter is a list of :class:`Plugin` instances.

(:count:`step`) Call each plugin's :meth:`on_plugins_loaded
<lino.core.plugins.Plugin.on_plugins_loaded>` method.

Note that the above steps happen while the :xfile:`settings.py` is *still being
loaded*. This means for example that you cannot access the :mod:`settings`
module in your :meth:`get_plugin_configs <Site.get_plugin_configs>` or
:meth:`on_plugins_loaded <lino.core.plugins.Plugin.on_plugins_loaded>` methods.
In this phase, everything in :mod:`lino.api.ad` is usable.


Data definition
===============

(:count:`step`) When Django has finished loading the :xfile:`settings.py` file,
it starts importing the :xfile:`models.py` module of each plugin. We call this
the :term:`data definition` phase. Everything in :mod:`lino.api.dd` is usable
during this step. :mod:`lino.api.rt` may be imported but should not be accessed
at global module level.

Site startup
============

(:count:`step`)   When Django has fully populated its models registry (imported
all :xfile:`models.py` modules), it finds :class:`lino.AppConfig` and runs its
`ready() method
<https://docs.djangoproject.com/en/5.0/ref/applications/#django.apps.AppConfig.ready>`__,
which does nothing more and nothing less than run :meth:`Site.startup`. This
kicks off the :term:`site analysis` phase. Which does the following:

(:count:`step`) Instantiate the kernel. :attr:`settings.SITE.kernel
<Site.kernel>` is now an instance of :class:`lino.core.kernel.Kernel` instead of
`None`.

(:count:`step`) Fill :attr:`Site.models`, an attrdict mapping the `app_label` of
each installed plugin to their curresponding :xfile:`models.py` module.

(:count:`step`) Emit the :data:`lino.core.signals.pre_startup` signal.

(:count:`step`) Run :meth:`pre_site_startup <lino.core.plugins.Plugin.pre_site_startup>` of each
plugin.

(:count:`step`) Run :meth:`Kernel.kernel_startup`, which does what's explained
in `Kernel startup`_ below.

(:count:`step`) Run :attr:`Site.do_site_startup`

(:count:`step`) Run :meth:`lino.core.plugins.Plugin.post_site_startup` on each plugin

(:count:`step`) Emit the :data:`lino.core.signals.post_startup` signal


Kernel startup
==============

(:count:`step`) Register :meth:`Site.shutdown` to :mod:`atexit` and stop signal handler.

(:count:`step`) Install a :class:`DisableDeleteHandler
<lino.core.ddh.DisableDeleteHandler>` for each model into
:attr:`Model._lino_ddh`.

(:count:`step`) Install :class:`lino.core.model.Model` attributes and methods
into raw Django Models that don't inherit from it.

(:count:`step`) Populate :attr:`Site.GFK_LIST`, a list of all :term:`generic
foreign key` fields in the database.

(:count:`step`) Import :attr:`Site.user_types_module`

(:count:`step`) Analyze ForeignKeys and populate the
:class:`DisableDeleteHandler <lino.core.ddh.DisableDeleteHandler>`.

(:count:`step`) Import :attr:`Site.workflows_module`

(:count:`step`) Run :meth:`lino.core.plugins.Plugin.before_analyze` on each
plugin

(:count:`step`) Emit the :data:`lino.core.signals.pre_analyze` signal

(:count:`step`) Run :meth:`lino.core.site.Site.setup_actions`

(:count:`step`) Import :attr:`Site.custom_layouts_module` if defined.

(:count:`step`) Call :meth:`lino.core.model.Model.on_analyze` on every model.

(:count:`step`) Call :meth:`lino.core.model.Model.collect_virtual_fields` on
every model. This attaches virtual fields to the model that declares them.

(:count:`step`) Run :meth:`lino.core.plugins.Plugin.before_actors_discover` on
each plugin.

(:count:`step`) Discover and initialize actors

(:count:`step`) Emit the :data:`lino.core.signals.post_analyze` signal

(:count:`step`) Run :meth:`lino.core.actors.Actor.after_site_setup` on each
actor

(:count:`step`) Emit the :data:`lino.core.signals.pre_ui_build` signal

(:count:`step`) Run :meth:`lino.core.plugins.Plugin.on_ui_init` on each plugin

Runtime
=======

(:count:`step`) When site startup has finished, we finally enter the
:term:`runtime` phase. Only now everything in :mod:`lino.api.rt` is usable.
