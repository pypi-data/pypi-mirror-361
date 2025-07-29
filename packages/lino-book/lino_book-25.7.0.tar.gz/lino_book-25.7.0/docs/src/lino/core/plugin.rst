================================
``lino.core.plugin``
================================

See also :doc:`/dev/plugins`.

.. .. currentmodule:: lino.api.ad
.. currentmodule:: lino.core.plugin

.. class:: Plugin

  The base class for all plugin descriptors.

  .. attribute:: verbose_name

    The verbose name of this plugin, as shown to the user.  This can be
    a lazily translated string.

  .. attribute:: short_name

    The abbreviated name of this plugin, shown to the user in places
    where shortness is important, e.g. as the label of the tabs of a
    detail layout.  This can be a lazily translated string. Defaults
    to :attr:`verbose_name`.

  .. attribute:: needs_plugins

    A list of names of plugins needed by this plugin.

    The default implementation of :meth:`get_required_plugins` returns this
    list.

  .. attribute:: needed_by

    If not None, then it is the Plugin instance that caused this plugin to
    automatically install.  As the application developer
    you do not set this yourself

  .. attribute:: extends_models

    If specified, a list of model names for which this app provides a
    subclass.

    For backwards compatibility this has no effect
    when :setting:`override_modlib_models` is set.

  .. attribute:: menu_group

    The name of another plugin to be used as menu group.

    See :meth:`get_menu_group`, :ref:`dev.xlmenu`.

  .. attribute:: media_base_url

    Remote URL base for media files.

  .. attribute:: media_name

    Either `None` (default) or a non-empty string with the name of the
    subdirectory of your :xfile:`media` directory which is expected to
    contain media files for this app.

    `None` means that there this app has no media files of her own.

    Best practice is to set this to the `app_label`.  Will be ignored
    if :attr:`media_base_url` is nonempty.

  .. attribute:: url_prefix

    The url prefix under which this plugin should ask to
    install its url patterns.

  .. attribute:: site_js_snippets

    List of js snippets to be injected into the `lino_*.js` file.

  .. attribute:: support_async

    Whether this plugin uses :class:`lino.core.utils.DelayedValue`.

  .. attribute:: renderer

    The renderer used by this plugin. See :doc:`/dev/rendering`.

  .. attribute:: hidden

    Whether this plugin is :attr:`hidden`.

    A hidden attribute is installed, but not visible.

  .. method:: is_hidden

    Whether this plugin is :attr:`hidden`.

  .. method:: hide

    Mark this plugin as :attr:`hidden`.

  .. attribute:: ui_handle_attr_name

    Currently implemented by :mod:`lino.modlib.extjs`,
    :mod:`lino.modlib.bootstrap3`.

  .. method:: __init__(self, site, app_label, app_name, app_module, needed_by, configs: dict)

    This is called when the Site object *instantiates*, i.e.  you may
    not yet import `django.conf.settings`.  But you get the `site`
    object being instantiated.

    Parameters:

    :site:       The :class:`Site` instance
    :app_label:  e.g. "contacts"
    :app_name:   e.g. "lino_xl.lib.contacts"
    :app_module: The module object corresponding to the :xfile:`__init__.py` file.

  .. method:: configure(self, **kw)

    Set the given parameter(s) of this Plugin instance.  Any number of
    parameters can be specified as keyword arguments.

    Raise an exception if caller specified a key that does not
    have a corresponding attribute.

  .. method:: get_required_plugins(self)

    Return a list of names of plugins needed by this plugin.

    The default implementation returns :attr:`needs_plugins`.

    Lino will automatically install these plugins if necessary.

    Note that Lino will add them *before* your plugin.

    Note that only the app_label (not the full plugin name) is used when
    testing whether a plugin is installed. In other words, if a plugin says
    it requires a plugin "stdlib.foo" and an application already has some
    plugin "mylib.foo" installed, then "mylib.foo" satisfies "stdlib.foo".


  .. method:: get_used_libs(self, html=None)

    Yield a series of tuples `(verbose_name, version, url)` that describe
    the libraries used by this Lino site.



  .. method:: get_site_info(self, ar=None)

    Return a string to show in :class:`lino.modlib.about.About`.

    TODO: move this and the :setting:`use_contacts` setting to ``about``.

  .. method:: on_init(self)

    This will be called when the Plugin is being instantiated (i.e.
    even before the :class:`Site` instantiation has finished. Used
    by :mod:`lino.modlib.users` to set :attr:`user_model`.

  .. method:: on_plugins_loaded(self, site)

    Called exactly once on each installed plugin, when the
    :class:`Site` has loaded all plugins, but *before* calling
    :meth:`setup_plugins`.  All this happens before settings are
    ready and long before the models modules start to load.

    This is used for initializing default values of plugin
    attributes that (a) depend on other plugins but (b) should be
    overridable in :meth:`lino.core.site.Site.setup_plugins`.

    For example :mod:`groups` uses this to set a default value to
    the :attr:`commentable_model` for :mod:`comments` plugin.

  .. method:: pre_site_startup(self, site)

    This is called exactly once when models are ready.

  .. method:: install_django_settings(self, site)

    Install Django settings

  .. method:: before_actors_discover(self)

    This is called exactly once during :term:`site startup`, when models are
    ready.  Used by `lino.modlib.help`


  .. method:: post_site_startup(self, site)

    This will be called exactly once, when models are ready.

  .. method:: extends_from(cls)

    Return the plugin from which this plugin inherits.

  .. method:: get_subdir(cls, name)

    Get the absolute path of the named subdirectory if it exists.

  .. method:: before_analyze(self)

    This is called during startup, when all models modules have been
    imported, and before Lino starts to analyze them.

  .. method:: on_ui_init(self, kernel)

    This is called when the kernel is being instantiated.

  .. method:: get_patterns(self)

    Override this to return a list of url patterns to be added to the
    Site's patterns.

  .. method:: get_requirements(self, site)

    Return a list of optionally required Python packages to be installed
    during :manage:`install`.

    See also :doc:`/topics/requirements`.

  .. method:: get_head_lines(cls, site, request)

    Yield or return a list of textlines to add to the `<head>` of the
    html page.


  .. method:: on_initdb(self, site, force=False, verbosity=1)

    This is called during SITE.build_site_cache().


  .. method:: get_menu_group(self)

    Return the plugin (a :class:`Plugin` instance) into the menu of which
    this plugin should add its menu commands. See :ref:`dev.xlmenu`.

    This returns `self` by default, unless

    - this plugin defines an explicit :attr:`menu_group`. In this
      case return the named plugin.

    - this plugin was automatically installed because some other
      plugin needs it. In this case return that other plugin.


  .. method:: setup_user_prefs(self, up)

    Called when a :class:`lino.core.userprefs.UserPrefs` get
    instantiated.


  .. method:: get_quicklinks(self)

    Return or yield a sequence of quick link descriptors to be added to the
    list of quick links.

    A :term:`quick link` descriptor is a string that identifies either an
    actor or a bound action.


  .. method:: setup_quicklinks(self, tb)

    Add quicklinks to the list of quick links.


  .. method:: get_dashboard_items(self, user)

    Return or yield a sequence of items to be rendered on the
    dashboard.

    Called by :meth:`lino.core.site.Site.get_dashboard_items`.

    Every item is expected to be either an instance of
    :class:`lino.core.dashboard.DashboardItem`, or a
    :class:`lino.core.actors.Actor`.

    Tables are shown with a limit of
    :attr:`lino.core.tables.AbstractTable.preview_limit` rows.


  .. method:: get_detail_url(self, ar, actor, pk, *args, **kw)

    Return the URL to the given database row.

    This is only a relative URL. Get the fully qualified URI by prefixing
    :attr:`lino.core.site.Site.server_url`.

    The extjs frontend overrides this and returns different URIs depending
    on whether `ar.request` is set or not.
