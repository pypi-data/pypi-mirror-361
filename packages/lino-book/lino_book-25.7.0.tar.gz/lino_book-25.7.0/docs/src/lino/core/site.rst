.. doctest docs/api/ad/site.rst

================================
``lino.core.site``
================================


.. currentmodule:: lino.core.site

This is the reference documentation about the :class:`Site` class. Subsections
are currently just a desperate attempt to bring some order into the chaos.

For introductions see :doc:`/dev/hello/index` and :doc:`/dev/site`.


.. contents::
    :depth: 1
    :local:


.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.min1.startup import *


Instantiation
=============

.. class:: Site

  In your :file:`settings.py` file you instantiate a subclass of this and assign
  that instance to a variable named :setting:`SITE`.

  This class is designed to be overridden by both :term:`application developers
  <application developer>` and :term:`server administrators <server
  administrator>`.


  .. method:: __init__(self, settings_globals=None, local_apps=[], **kwargs)

    `settings_globals` is the `globals()` dictionary of the
    :xfile:`settings.py`.

    `local_apps` is used internally for testing.


Settings
========

.. class:: Site
  :no-index:

  .. attribute:: master_site

    Another Site instance to be used as the master for this site. Setting this
    attribute turns this site into a :term:`satellite site` of its master site.

  .. attribute:: show_internal_field_names

    Whether the internal field names should be visible.  ExtUI
    implements this by prepending them to the tooltip, which means
    that :attr:`use_quicktips` must also be `True`.  Default is
    `True`.

  .. attribute:: demo_fixtures

    The list of fixtures to be loaded by the :cmd:`pm prep`
    command.  See :ref:`demo_fixtures`.

  .. attribute:: is_demo_site

    Whether this site runs in :term:`demo mode`.

    Default value is `False`.  On a :term:`production site` you will of course
    take care to leave this to `False`.

    See also :attr:`demo_fixtures` and :attr:`the_demo_date` and
    :attr:`quick_startup`.


  .. attribute:: the_demo_date

    A constant date to be used as reference by :meth:`today` and
    :meth:`demo_date`.

    Default value is `None`.  If this is set, Lino shows a welcome message of
    style "We are running with simulated date set to Friday 22 May 2015."

    This is either `None` or a :class:`datetime.date` object. If your
    :xfile:`settings.py` specifies it as an :class:`int` or a :class:`str`, Lino
    converts it at :term:`site startup` to a :class:`datetime.date` using
    :func:`rstgen.utils.i2d`.

    Many :term:`demo projects <demo project>` have this set so that
    :term:`tested documents <tested document>` can rely on a constant reference
    date.


Optional features
=================

.. class:: Site
  :no-index:


  .. attribute:: use_jasmine

    Whether to use the `Jasmine <https://github.com/pivotal/jasmine>`_
    testing library.


  .. attribute:: jasmine_root

    Path to the Jasmine root directory.  Only used on a development
    server if the `media` directory has no symbolic link to the
    Jasmine root directory and only if :attr:`use_jasmine` is True.


  .. attribute:: use_quicktips

    Whether to make use of `Ext.QuickTips
    <http://docs.sencha.com/ext-js/3-4/#!/api/Ext.QuickTips>`_ for
    displaying :ref:`help_texts` and internal field names (if
    :attr:`show_internal_field_names`).


  .. attribute:: use_css_tooltips

    Whether to make use of CSS tooltips
    when displaying help texts defined in :class:`lino.models.HelpText`.


  .. attribute:: use_vinylfox

    Whether to use VinylFox extensions for HtmlEditor.
    This feature was experimental and doesn't yet work (and maybe never will).
    See `/blog/2011/0523`.




Formatting
==========

.. class:: Site
  :no-index:

  .. attribute:: decimal_separator

    Set this to either ``'.'`` or ``','`` to define wether to use comma
    or dot as decimal point separator when entering a `DecimalField`.


  .. attribute:: decimal_group_separator

    Decimal group separator for :meth:`decfmt`.


  .. attribute:: time_format_strftime

    Format (in strftime syntax) to use for displaying dates to the user.
    If you change this setting, you also need to override :meth:`parse_time`.



  .. attribute:: date_format_strftime


    Format (in strftime syntax) to use for displaying dates to the user.
    If you change this setting, you also need to override :meth:`parse_date`.


  .. attribute:: date_format_regex


    Format (in JavaScript regex syntax) to use for displaying dates to
    the user.  If you change this setting, you also need to override
    :meth:`parse_date`.


  .. attribute:: datetime_format_strftime

    Format (in strftime syntax) to use for formatting timestamps in
    AJAX responses.  If you change this setting, you also need to
    override :meth:`parse_datetime`.


  .. attribute:: datetime_format_extjs

    Format (in ExtJS syntax) to use for formatting timestamps in AJAX
    calls.  If you change this setting, you also need to override
    :meth:`parse_datetime`.

.. method:: get_letter_date_text(self, today=None)

      Returns a string like "Eupen, den 26. August 2013".

      >>> settings.SITE.get_letter_date_text()
      'Vigala, 23 October 2014'

      The place name in above string comes from the :term:`site owner`:

      >>> dd.plugins.contacts.site_owner.city
      Place #54 ('Vigala')

.. method:: decfmt(self, v, places=2, **kw)

      Format a Decimal value using :func:`lino.utils.moneyfmt`, but
      applying the site settings
      :attr:`lino.Lino.decimal_group_separator` and
      :attr:`lino.Lino.decimal_separator`.

.. method:: format_currency(self, *args, **kwargs)

      Return the given number as a string formatted according to the
      :attr:`site_locale` setting on this site.

      All arguments are forwarded to `locale.locale()
      <https://docs.python.org/3/library/locale.html#locale.currency>`__.


      >>> settings.SITE.site_locale
      'en_GB.UTF-8'
      >>> dd.format_currency(1234)
      '£1234.00'

  .. method:: parse_date(self, s)

        Convert a string formatted using :attr:`date_format_strftime` or
        :attr:`date_format_extjs` into a `(y,m,d)` tuple (not a
        `datetime.date` instance).  See `/blog/2010/1130`.

  .. method:: parse_time(self, s)

        Convert a string into a `datetime.time` instance using regex.
        only supports hours and min, not seconds.

  .. method:: parse_datetime(self, s)

        Convert a string formatted using :attr:`datetime_format_strftime`
        or :attr:`datetime_format_extjs` into a `datetime.datetime`
        instance.


Used at runtime
===============

.. class:: Site
  :no-index:

  .. attribute:: plugins

    An :class:`AttrDict <atelier.utils.AttrDict>` with one entry
    for each installed plugin, mapping the `app_label` of every
    plugin to the corresponding :class:`lino.core.plugin.Plugin`
    instance.

    This attribute is automatically filled by Lino and available as
    :attr:`dd.plugins <lino.api.dd>` already before Django starts to
    import :xfile:`models.py` modules.

  .. attribute:: modules

    Old name for :attr:`models`.  Deprecated.

  .. attribute:: models

    An :class:`AttrDict <atelier.utils.AttrDict>` which maps every
    installed `app_label` to the corresponding :xfile:`models.py`
    module object.

    This is also available as the shortcut :attr:`rt.models
    <lino.api.rt.models>`.

    See :doc:`/dev/plugins`

  .. method:: is_installed(self, app_label)

        Return `True` if :setting:`INSTALLED_APPS` contains an item
        which ends with the specified `app_label`.

  .. method:: makedirs_if_missing(self, dirname)

        Make missing directories if they don't exist and if
        :attr:`make_missing_dirs` is `True`.

  .. method:: today(self, *args, **kwargs)

        Almost the same as :func:`datetime.date.today`.

        One difference is that the system's *today* is replaced by
        :attr:`the_demo_date` if that attribute is set.

        Another difference is that arguments can be passed to add some
        offset. See :func:`atelier.utils.date_offset`.

        This feature is being used in many test cases where e.g. the
        age of people would otherwise change.


  .. method:: now(self)

        Return the current datetime, considering the current :term:`time zone`,
        :class:`system.SiteConfig.simulate_today` and :attr:`the_demo_date`.

  .. method:: demo_date(self, *args, **kwargs)

    Deprecated. Should be replaced by :meth:`today`.  Compute a date
    using :func:`lino.utils.date_offset` based on the process
    startup time (or :attr:`the_demo_date` if this is set).

    Used in Python fixtures and unit tests.


  .. method:: welcome_text(self)

        Return the text to display in a console window when this
        application starts.


  .. method:: using_text(self)

        Return the text to display in a console window when Lino starts.


  .. method:: site_version(self)

        Return the name of the application running on this site, including the
        version (if a version is specified).

        Used in footnote or header of certain printed documents.


Startup
=======

Used internally during startup.

.. class:: Site
  :no-index:

  .. method:: init_before_local(self, settings_globals, local_apps)

        If your :attr:`project_dir` contains no :xfile:`models.py`, but
        *does* contain a `fixtures` subdir, then Lino automatically adds this
        as a local fixtures directory to Django's :setting:`FIXTURE_DIRS`.

        But only once: if your application defines its own local
        fixtures directory, then this directory "overrides" those of
        parent applications. E.g. lino_noi.projects.care does not want
        to load the application-specific fixtures of
        lino_noi.projects.team.

  .. method:: get_middleware_classes(self)

        Yields the strings to be stored in
        the :setting:`MIDDLEWARE_CLASSES` setting.

        In case you don't want to use this method for defining
        :setting:`MIDDLEWARE_CLASSES`, you can simply set
        :setting:`MIDDLEWARE_CLASSES` in your :xfile:`settings.py`
        after the :class:`Site` has been instantiated.

        `Django and standard HTTP authentication
        <https://stackoverflow.com/questions/152248/can-i-use-http-basic-authentication-with-django>`_


  .. method:: load_plugins(self)

        Load all plugins and build the :setting:`INSTALLED_APPS` setting
        for Django.

        This includes a call to :meth:`get_plugin_modifiers` and
        :meth:`get_installed_plugins`.



  .. method:: get_requirements(self)

        Collect requirements from plugins. Add some more requirements which
        depend on options in the local :xfile:`settings.py` file.


  .. method:: setup_plugins(self)

        Deprecated. Use :meth:`get_plugin_configs` instead.

        This method is called exactly once during site startup, after
        :meth:`load_plugins` but before populating the models
        registry.

        See :ref:`dev.plugins`.


  .. method:: setup_cache_directory(self)

        When :envvar:`LINO_CACHE_ROOT` is set, Lino adds a stamp file
        called :xfile:`lino_cache.txt` to every project's cache
        directory in order to avoid duplicate use of same cache
        directory.

        .. xfile:: lino_cache.txt

            A small text file with one line of text which contains the
            path of the project which uses this cache directory.

  .. method:: set_user_model(self, spec)

        This can be called during the :meth:`on_init
        <lino.core.plugin.Plugin.on_init>` of plugins that provide
        user management (the only plugin that does this is currently
        :mod:`lino.modlib.users`).

  .. method:: get_auth_method(self)

        Returns the authentication method used on this site. This is one of
        `None`, `'remote'` or `'session'`.

        It depends on the values in
        :attr:`user_model`,
        :attr:`default_user` and
        :attr:`remote_user_header`.

        It influences the results of
        :meth:`get_middleware_classes` and
        :meth:`get_installed_plugins`, and the content of
        :setting:`AUTHENTICATION_BACKENDS`.

  .. method:: startup(self)

        Start up this Site.

        You probably don't want to override this method as it might be
        called several times.  e.g. under mod_wsgi: another thread has
        started and not yet finished `startup()`.

        If you want to run custom code on site startup, override
        :meth:`do_site_startup`.

  .. method:: do_site_startup(self)

        This method is called exactly once during site startup, just
        between the pre_startup and the post_startup signals.  A hook
        for subclasses.

        TODO: rename this to `on_startup`?


  .. method:: get_settings_subdirs(self, subdir_name)

        Yield all (existing) directories named `subdir_name` of this Site's
        project directory and its inherited project directories.

  .. method:: setup_model_spec(self, obj, name)

        If the value of the named attribute of `obj` is a string, replace
        it by the model specified by that string.

        Example usage::

            # library code:
            class ThingBase(object):
                the_model = None

                def __init__(self):
                    settings.SITE.setup_model_spec(self, 'the_model')

            # user code:
            class MyThing(ThingBase):
                the_model = "contacts.Partner"


  .. method:: on_each_app(self, methname, *args)


        Call the named method on the :xfile:`models.py` module of each
        installed app.

        Note that this mechanism is deprecated. It is still used (on
        names like ``setup_workflows`` and ``setup_site``) for
        historical reasons but will disappear one day.


  .. method:: for_each_app(self, func, *args, **kw)

        Call the given function on each installed plugin.  Successor of
        :meth:`on_each_app`.

        This also loops over plugins that don't have a models module
        and the base plugins of plugins which extend some plugin.

  .. method:: install_migrations(self, *args)

        See :func:`lino.utils.dpy.install_migrations`.


  .. method:: setup_actions(self)


        Hook for subclasses to add or modify actions.


  .. method:: get_used_libs(self, html=None)

        Yield a list of (name, version, url) tuples describing the
        third-party software used on this site.

        This function is used by :meth:`using_text` and
        :meth:`welcome_html`.



  .. method:: apply_languages(self):

        This function is called when a Site object gets instantiated,
        i.e. while Django is still loading the settings. It analyzes
        the :attr:`languages` attribute and converts it to a tuple of
        :data:`LanguageInfo` objects.



  .. method:: setup_languages(self)

        Reduce Django's :setting:`LANGUAGES` to my `languages`.
        Note that lng.name are not yet translated, we take these
        from `django.conf.global_settings`.



Unclassified
============

.. class:: Site
  :no-index:

  .. method:: is_abstract_model(self, module_name, model_name)


        Return True if the named model is declared as being extended by
        :attr:`lino.core.plugin.Plugin.extends_models`.

        Typical usage::

            class MyModel(dd.Model):
                 class Meta:
                     abstract = dd.is_abstract_model(__name__, 'MyModel')

        See :doc:`/dev/plugin_inheritance`.



  .. method:: is_imported_partner(self, obj)

        Return whether the specified
        :class:`Partner <ml.contacts.Partner>` instance
        `obj` is to be considered as imported from some legacy database.


  .. method:: site_header(self)

        Used in footnote or header of certain printed documents.

        The convention is to call it as follows from an appy.pod template
        (use the `html` function, not `xhtml`)
        ::

          do text
          from html(settings.SITE.site_header())

        Note that this is expected to return a unicode string possibly
        containing valid HTML (not XHTML) tags for formatting.



  .. method:: get_dashboard_items(self, user)

        Expected to yield a sequence of items to be rendered on the
        dashboard (:xfile:`admin_main.html`).

        The default implementation calls :meth:`get_dashboard_items
        <lino.core.plugin.Plugin.get_dashboard_items>` on every
        installed plugin and yields all items.

        The items will be rendered in that order, except if
        :mod:`lino.modlib.dashboard` is installed to enable per-user
        customized dashboard.


  .. attribute:: site_config


        This property holds a cached version of the one and only
        :class:`SiteConfig <lino.modlib.system.SiteConfig>` row
        that holds site-wide database-stored and web-editable Site
        configuration parameters.

        If no instance exists (which happens in a virgin database), we create it
        using default values from :attr:`site_config_defaults`.

        This is `None` when :mod:`lino.modlib.system` is not installed.

        It can also be `None` when startup is not done, which can happen e.g.
        on an asgi web server.

  .. method:: get_config_value(self, name, default=None)

        Return the value of the named SiteConfig field.

        When :attr:`site_config` is `None` for whatever reason, this  returns
        the specified `default` value, which defaults to `None`
        (:attr:`site_config_defaults` is *not* looked up in this case).


  .. method:: clear_site_config(self)

        Clear the cached SiteConfig instance.

        This is needed e.g. when the test runner has created a new
        test database.


  .. attribute:: quicklinks

        The list of `quick links`.

        This is lazily created when first accessed.


  .. method:: get_quicklink_items(self, user_type)

        Yield the quick links that are visible for the given user type.


  .. method:: get_quicklinks(self)

        Return or yield a sequence of quick link descriptors to be added to the
        list of quick links.

        Override this to define application-specific quick links.


  .. method:: setup_quicklinks(self, unused, tb)

        Customize the list of :term:`quick links <quick link>`.
        Override this to define application-specific quick links.

        Default implementation calls :meth:`get_quicklinks
        <lino.core.plugins.Plugin.get_quicklinks>` and :meth:`setup_quicklinks
        <lino.core.plugins.Plugin.setup_quicklinks>` for each installed plugin.

        The quicklinks yielded by :meth:`get_quicklinks
        <lino.core.plugins.Plugin.get_quicklinks>` will be added before
        calling :meth:`setup_quicklinks
        <lino.core.plugins.Plugin.setup_quicklinks>`.


  .. method:: get_site_menu(self, user_type)

        Return this site's main menu for the given UserType.
        Must be a :class:`lino.core.menus.Toolbar` instance.
        Applications usually should not need to override this.


  .. method:: setup_menu(self, user_type, main)

        Set up the application's menu structure.

        See :doc:`/dev/menu` and :doc:`/dev/xlmenu`.


  .. method:: get_main_html(self, ar, **context)

        Return a chunk of html to be displayed in the main area of the
        admin index.  The default
        implementation renders the :xfile:`admin_main.html` template.


  .. method:: build_site_cache(self, force=False, later=False, verbosity=1)

        Populate the :term:`site cache`, especially the
        :xfile:`lino*.js` files, one per user :term:`user type` and language.

        - ``force``: rebuild the files even if they are up to date

        - ``later``: don't rebuild now, just touch the :xfile:`settings.py` so
          that they get rebuild next time.

  .. method:: get_top_links(self, ar)

        Creates links/actions to put into :term:`React front end` top bar.

  .. method:: add_top_link_generator(self, func)

        Add the given callable `func` as a "top link generator".

  .. method:: get_welcome_messages(self, ar)

        Yields a list of "welcome messages" (see
        :meth:`lino.core.actors.Actor.get_welcome_messages`) of all
        actors.  This is being called from :xfile:`admin_main.html`.

  .. method:: add_welcome_handler(self, func, actor=None, msg=None)

        Add the given callable as a "welcome handler".  Lino will call
        every welcome handler for every incoming request, passing them
        a :class:`BaseRequest <lino.core.requests.BaseRequest>`
        instance representing this request as positional argument.
        The callable is expected to yield a series of messages
        (usually either 0 or 1). Each message must be either a string
        or a :class:`E.span <etgen.html.E>` element.

  .. method:: welcome_html(self, ui=None)

        Return a HTML version of the "This is APPLICATION
        version VERSION using ..." text. to be displayed in the
        About dialog, in the plain html footer, and maybe at other
        places.


  .. method:: login(self, username=None, **kw)

        Open a session as the user with the given `username`.

        For usage from a shell or a tested document.  Does not require
        any password because when somebody has command-line access we
        trust that she has already authenticated.

        It returns a
        :class:`BaseRequest <lino.core.requests.BaseRequest>` object.


  .. method:: lookup_filter(self, fieldname, value, **kw)

        Return a `models.Q` to be used if you want to search for a given
        string in any of the languages for the given babel field.


  .. method:: get_plugin_setting(self, plugin_name, option_name, *default)

        Return the given plugin setting if the plugin is installed, otherwise
        the provided default value.


  .. attribute:: beid_protocol

    Until 20180926 this was a string like e.g. 'beid' in order to
    use a custom protocol for reading eid cards.  Now it is
    deprecated.  Use :attr:`lino_xl.lib.beid.Plugin.urlhandler_prefix`
    instead.

  .. attribute:: quantity_max_length

    The default value for `max_length` of quantity fields.

  .. attribute:: upload_to_tpl

    The value to use as
    `upload_to
    <https://docs.djangoproject.com/en/5.0/ref/models/fields/#django.db.models.FileField.upload_to>`__
    for the :attr:`Upload.file` field.

    Default value is ``'uploads/%Y/%m'``.


  .. attribute:: auto_fit_column_widths

    The default value for the :attr:`auto_fit_column_widths
    <lino.core.tables.AbstractTable.auto_fit_column_widths>` of tables
    in this application.


  .. attribute:: site_locale


    The `locale <https://docs.python.org/3/library/locale.html>`__ to
    use for certain localized things on this site.

    Used by :meth:`format_currency`.

    This should be a string of type '<language>_<country>.<encoding>',
    and it must have been generated previously.  For example::

        sudo locale-gen de_BE.utf8


  .. attribute:: confdirs


    Pointer to the config directories registry.
    See :ref:`config_dirs` and :mod:`lino.utils.config`.
    Lino sets this attribute during site startup.


  .. attribute:: kernel


    This attribute is available only after :meth:`startup`.
    See :mod:`lino.core.kernel`.



  .. attribute:: readonly

    Setting this to `True` turns this site in a readonly site.  This
    means that :setting:`DATABASES` must point to the
    :setting:`DATABASES` of some other (non-readonly) site, and that
    :manage:`initdb` will do nothing.



  .. attribute:: hoster_status_url

    This is mentioned in :xfile:`500.html`.



  .. attribute:: description


    A multi-line plain text description of up to 250 characters.

    Common practice is to fill this from your SETUP_INFO.

    It is listed on https://www.lino-framework.org/apps.html

  .. attribute:: make_missing_dirs

    Set this to `False` if you don't want Lino to automatically create
    missing directories when needed.  If this is False, Lino will
    raise an exception in these cases, asking you to create it
    yourself.



  .. attribute:: site_dir

    The directory where Lino stores local files.

    See :ref:`dg.topics.local_files`.


  .. attribute:: project_dir

    The :term:`Django project directory` for this site.

    See :ref:`dg.topics.local_files`.



  .. attribute:: media_root

    The root directory at which to build the JavaScript and json cache files.
    See :ref:`dg.topics.local_files`.


  .. attribute:: project_name

    A nickname for this project.

    This is used only when :envvar:`LINO_CACHE_ROOT` is set, and only to set the
    :attr:`site_dir`.  In that case all Lino projects in a given repository must
    have a unique project name.

    If this is `None`, Lino will find a default value by splitting
    :attr:`project_dir` and taking the last part (or the second-last if the last
    part is 'settings'.



  .. attribute:: django_settings

    This is a reference to the `globals()` dictionary of your
    :xfile:`settings.py` file (the one you provided when instantiating
    the Site object).



  .. attribute:: startup_time


    The time when this Site has been instantiated,
    in other words the startup time of this Django process.
    Don't modify this.

  .. attribute:: top_level_menus

    The list of top-level menu items.
    See :doc:`/dev/menu` and :doc:`/dev/xlmenu`.


  .. attribute:: loading_from_dump

    Whether the process is currently loading data from a Python dump.

    When loading from a python dump, application code should not
    generate certain automatic data because that data is also part of
    the dump.

    This is normally `False`, but a Python dump created with
    :cmd:`pm dump2py` explicitly calls :meth:`install_migrations`,
    which sets this to `True`.

    Application code should not change this setting except for certain
    special test cases.



  .. attribute:: project_model


    Specifies the application's project model.

    A project in this context means what the users consider "the central most
    important thing that is used to classify most other things".  For example in
    :ref:`avanti` the "project" is a Client while in :ref:`tera` it is a
    therapy.

    This can be either `None` (the default value) or the full name of the model
    used as "central project model" in this application.

    If this is not `None`, all models that inherit from :class:`ProjectRelated
    <lino.mixins.ProjectRelated>` will have an additional ForeignKey to this
    model.

    TODO: convert this into a plugin setting of the office plugin?


  .. attribute:: user_model


    The database model used for users.
    This is automatically set to ``'users.User'`` when
    :mod:`lino.modlib.users` is installed.

    Default value is `None`, meaning that this application has no user
    management.  See also :meth:`set_user_model`

    See also :doc:`/plugins/users`.


  .. attribute:: auth_middleware


    Override used authorisation middlewares with supplied tuple of
    middleware class names.

    If None, use logic described in :ref:`admin.auth`


  .. attribute:: never_build_site_cache

    Probably deprecated. Set this to `True` if you want that Lino never
    (re)builds the :term:`site cache`, even when asked.  This can be useful on a
    development server when you are debugging directly on the generated
    :xfile:`lino*.js`.  Or for certain unit test cases.



  .. attribute:: keep_erroneous_cache_files

    Whether to keep partly generated files in the the :term:`site cache`.


  .. attribute:: site_config_defaults

    Default values to be used when creating the :attr:`site_config`.

    Usage example::

      site_config_defaults = dict(default_build_method='appypdf')




  .. attribute:: use_experimental_features

    Whether to include "experimental features". Deprecated.
    lino_xl.lib.inspect


  .. attribute:: use_new_unicode_symbols

    Whether to use "new" unicode symbols (e.g. from the `Miscellaneous
    Symbols and Pictographs
    <https://en.wikipedia.org/wiki/Miscellaneous_Symbols_and_Pictographs>`__
    block) which are not yet implemented in all fonts.

    Currently used by :mod:`lino_noi.lib.noi.workflows`



  .. attribute:: use_silk_icons


    If this is `True`, certain Lino plugins use the deprecated `silk
    icons library <http://www.famfamfam.com/lab/icons/silk/>`__ for
    representing workflows.

    The recommended but not yet fully implemented "modern" style is to
    use unicode symbols instead of icons.


  .. attribute:: use_java


    A site-wide option to disable everything that needs Java.  Note
    that it is up to the plugins which include Java applications to
    respect this setting. Usage example is :mod:`lino_xl.lib.beid`.


  .. attribute:: use_solr

    Whether to use solr backend server for search document indexing.

  .. attribute:: default_build_method

    The default build method to use when rendering printable documents.

    This is the last default value, used only when
    :attr:`default_build_method
    <lino.modlib.system.SiteConfig.default_build_method>` in
    :class:`SiteConfig <lino.modlib.system.SiteConfig>` is
    empty.

  .. attribute:: django_admin_prefix


    The prefix to use for Django admin URLs.
    Leave this unchanged as long as :srcref:`docs/tickets/70` is not solved.


  .. attribute:: calendar_start_hour


    The first hour of a work day.

    Limits the choices of a :class:`lino.core.fields.CalendarTimeField`.


  .. attribute:: calendar_end_hour


    The last hour of a work day.

    Limits the choices of a :class:`lino.core.fields.CalendarTimeField`.


  .. attribute:: time_format_extjs


    Format (in ExtJS syntax) to use for displaying dates to the user.
    If you change this setting, you also need to override :meth:`parse_time`.

    Default value is ``'H:i'``.

    >>> settings.SITE.time_format_extjs
    'H:i'


  .. attribute:: alt_time_formats_extjs

    Alternative time entry formats accepted by ExtJS time widgets.

    ExtJS default is:

        "g:ia|g:iA|g:i a|g:i A|h:i|g:i|H:i|ga|ha|gA|h a|g a|g A|gi|hi|gia|hia|g|H|gi a|hi a|giA|hiA|gi A|hi A"

    Lino's extended default also includes:

        "Hi" (1900) and "g.ia|g.iA|g.i a|g.i A|h.i|g.i|H.i" (Using . in replacement of ":")



  .. attribute:: date_format_extjs

    Format (in ExtJS syntax) to use for displaying dates to the user.
    If you change this setting, you also need to override :meth:`parse_date`.

    Default value is ``'d.m.Y'``.

    >>> settings.SITE.date_format_extjs
    'd.m.Y'


  .. attribute:: alt_date_formats_extjs

    Alternative date entry formats accepted by ExtJS Date widgets.

    >>> settings.SITE.alt_date_formats_extjs
    'd/m/Y|Y-m-d'



  .. attribute:: uppercase_last_name


    Whether last name of persons should (by default) be printed with
    uppercase letters.

    See :mod:`lino.test_apps.human`


  .. attribute:: preview_limit

    Default value for the :attr:`preview_limit
    <lino.core.tables.AbstractTable.preview_limit>` parameter of all
    tables who don't specify their own one.  Default value is 15.

    >>> settings.SITE.preview_limit
    15


  .. attribute:: textfield_format

    The default format for :term:`rich textfields <rich textfield>`.  Valid
    choices are ``'plain'`` and ``'html'``.

    See :doc:`/dev/textfield`.

  .. attribute:: textfield_bleached

    Default value for `RichTextField.textfield_bleached`.

    See :doc:`/dev/bleach`.

  .. attribute:: default_user

    Username of the user to be used for all incoming requests.  Setting
    this to a nonempty value will disable authentication on this site.
    The special value `'anonymous'` will cause anonymous requests
    (whose `user` attribute is the :class:`AnonymousUser
    <lino.core.auth.utils.AnonymousUser>` singleton).

    See also :meth:`get_auth_method`.

    This setting should be `None` when :attr:`user_model` is `None`.

  .. attribute:: remote_user_header

    The name of the header (set by the web server) that Lino should
    consult for finding the user of a request.

    The default value `None` means that HTTP authentication is not used.
    Apache's default value is ``"REMOTE_USER"``.

    No longer used since 20240518.


  .. attribute:: use_eid_applet

    Whether to include functionality to read Belgian id cards using the
    official `eid-applet <http://code.google.com/p/eid-applet>`_.
    This option is experimental and doesn't yet work.  See
    `/blog/2012/1105`.


  .. attribute:: use_esteid

    Whether to include functionality to read Estonian id cards.  This
    option is experimental and doesn't yet work.


  .. attribute:: use_awesome_uploader

    Whether to use AwesomeUploader.
    This option was experimental and doesn't yet work (and maybe never will).


  .. attribute:: verbose_client_info_message

    Set this to True if actions should send debug messages to the client.
    These will be shown in the client's JavaScript console only.


  .. attribute:: stopsignal

    The signal to which the log server should register its shutdown handler.

    This is used to log an info message when a process ends
    (:ref:`history_aware_logging`).

    On a production server with :data:`lino.modlib.linod.use_channels` set to
    `True`, this must be the same signal as the ``stopsignal`` setting in the
    ``program`` section of your `supervisor config
    <https://supervisord.org/configuration.html?highlight=stopsignal#program-x-section-values>`__.

    >>> settings.SITE.stopsignal
    'SIGTERM'

  .. attribute:: help_email


    An e-mail address where users can get help. This is included in
    :xfile:`admin_main.html`.


  .. attribute:: catch_layout_exceptions


    Lino usually catches any exception during startup (in
    :func:`create_layout_element
    <lino.core.layouts.create_layout_element>`) to report errors of
    style "Unknown element "postings.PostingsByController
    ('postings')" referred in layout <PageDetail on publisher.Pages>."

    Setting this to `False` is useful when there's some problem
    *within* the framework.


  .. attribute:: strict_master_check



    Whether to raise BadRequest when master instance is not correctly specified.
    This was introducted in March 2023 and is not yet implemented everywhere.



  .. attribute:: strict_dependencies


    This should be True unless this site is being used just for autodoc
    or similar applications.



  .. attribute:: strict_choicelist_values


    Whether invalid values in a ChoiceList should raise an exception.

    This should be `True` except for exceptional situations.  Setting this to
    `True` won't allow you to store invalid choicelist values in the database,
    but at least Lino will not raise an exception as soon as it reads an invalid
    value from existing data.  This can happen e.g. after a code upgrade without
    data migration.  In such a situation you may want to run
    :xfile:`make_snapshot.sh` in order to migrate the data.



  .. attribute:: csv_params


    Site-wide default parameters for CSV generation.  This must be a
    dictionary that will be used as keyword parameters to Python
    `csv.writer()
    <http://docs.python.org/library/csv.html#csv.writer>`_

    Possible keys include:

    - encoding :
      the charset to use when responding to a CSV request.
      See
      http://docs.python.org/library/codecs.html#standard-encodings
      for a list of available values.

    - many more allowed keys are explained in
      `Dialects and Formatting Parameters
      <http://docs.python.org/library/csv.html#csv-fmt-params>`_.


  .. attribute:: quick_startup


    Whether to skip startup operations that are useful during development but
    not one production site.


  .. attribute:: override_modlib_models

    A dictionary that maps model class names to the plugin which
    overrides them.

    This is automatically filled at startup.  You can inspect it, but
    you should not modify it.  Needed for :meth:`is_abstract_model`.

    The challenge is that we want to know exactly where every model's
    concrete class will be defined *before* actually starting to
    import the :xfile:`models.py` modules.  That's why we need
    :attr:`extends_models <lino.core.plugin.Plugin.extends_models>`.

    This can be tricky, see e.g. 20160205.


  .. attribute:: installed_plugin_modules


    Used internally by :meth:`is_abstract_model`.  Don't modify.

    A set of the full Python paths of all imported plugin modules. Not
    just the plugin modules themselves but also those they inherit
    from.


Utilities
=========

.. function:: to_locale(language)

  Simplified copy of `django.utils.translation.to_locale`, but we need it while
  the `settings` module is being loaded, i.e. we cannot yet import
  django.utils.translation.  Also we don't need the `to_lower` argument.


.. class:: TestSite(Site)

    Used to simplify doctest strings because it inserts default values
    for the two first arguments that are mandatory but not used in our
    examples.

    Example::

      from lino.core.site import Site
      Site(globals(), ...)

      from lino.core.site import TestSite as Site
      Site(...)


Satellite sites
===============

.. glossary::

  satellite site

    A Lino site that has its :attr:`lino.core.site.Site.master_site`
    pointing to another Lino site.

    A satellite site shares the following settings with it master:
    :setting:`DATABASES` and :setting:`SECRET_KEY` and the :attr:`site_dir
    <lino.core.site.Site.site_dir>`



See also
========

- :doc:`/dev/site`
- :doc:`/dev/plugins`
- :doc:`/dev/languages`
