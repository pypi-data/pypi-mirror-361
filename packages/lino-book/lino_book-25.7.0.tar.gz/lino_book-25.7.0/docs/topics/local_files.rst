.. _dg.topics.local_files:

==============================
Lino and local files
==============================

.. currentmodule:: lino.core.site

.. contents::
  :local:


``site_dir`` and ``project_dir``
================================

Lino sets these two attributes automatically when the :class:`Site` initializes.
You should not override them.

:attr:`Site.project_dir` is the directory containing your :xfile:`settings.py`
file. Or more precisely the directory containing the :term:`source file` of your
:envvar:`DJANGO_SETTINGS_MODULE`. When using a *settings package*,
:attr:`Site.project_dir` points to the :file:`settings` subdir of what
:ref:`getlino` calls the project directory.

:attr:`Site.site_dir` is usually the same as :attr:`Site.project_dir`, except in
the following cases:

- When a :attr:`Site.master_site` is given, the slave uses the
  :attr:`Site.site_dir` of the master.

- When an environment variable :envvar:`LINO_CACHE_ROOT` is defined, Lino sets
  the :attr:`Site.site_dir` to :envvar:`LINO_CACHE_ROOT` +
  :attr:`Site.project_name`. This is used in CI environments where we use
  settings from a code repository (e.g. book) and don't want to write to the
  repository itself.

The :attr:`site_dir` is the root for some subdirectories with special meaning:

- a :xfile:`log` directory will activate logging to a :xfile:`lino.log` file.
- a :xfile:`migrations` directory will activate Django migrations.
- a :xfile:`config` directory will be added to the config search path. See local config files.
- a :xfile:`media` directory is the default value for :setting:`MEDIA_ROOT`
- a :xfile:`static_root` directory is the default value for :setting:`STATIC_ROOT`.

Lino sets the :setting:`MEDIA_ROOT` to ``site_dir / 'media'`` and the
:setting:`STATIC_ROOT` to ``site_dir / 'static_root'``.

The :attr:`site_dir` is also where the  :xfile:`default.db` file sits when
using sqlite.

The site cache
==============

.. glossary::

  site cache

    The directory where Lino automatically generates certain files to be served
    as media files.

Both the :term:`ExtJS front end` and the :term:`React front end` :file:`*.js` or
:file:`*.json` files in the :term:`site cache`.

The :term:`site cache` sits below :attr:`Site.media_root`.


About ``LINO_CACHE_ROOT``
=========================

When a :attr:`Site.master_site` is specified, the slave site uses the
:term:`site cache` of the master.

The front end populates the site cache either "late" or "early", where  "late"
means on each incoming request, and "early" means during explicit
:manage:`collectstatic`, :manage:`makehelp` and :manage:`buildcache` command.
On a production site we want to call it "early": we explicitly run
:manage:`collectstatic`, :manage:`makehelp` and :manage:`buildcache` after an
upgrade, and don't want Lino to waste resources by checking whether it's done
again and again for every incoming request. But when developing, we don't want
Lino to generate all js files (for all user types and all languages) for every
little change in the source code.

The :attr:`lino.core.site.Site.build_js_cache_on_startup` attribute is `False`.

- with `force=True` by :manage:`buildcache` or when
  :class:`lino.modlib.system.BuildSiteCache` is run.


On a :term:`production site`, :attr:`Site.build_js_cache_on_startup` should be
`True` for best performance, but during development and testing this is not
necessary, so default value is `False`, which means that each file is built upon
need (when a first request comes in).

You can also set :attr:`Site.build_js_cache_on_startup` to `None`, which means
that Lino decides automatically during startup: it becomes `False` if either
:func:`lino.core.utils.is_devserver` returns True or :setting:`DEBUG` is set.

.. envvar:: LINO_BUILD_CACHE_ON_STARTUP

    If a variable of that name is set, then Lino will override the
    code value and set :attr:`build_js_cache_on_startup` to True.

When some exception occurs while populating the site cache Lino usually removes
the partly generated file to make sure that it will try to generate it again
(and report the same error message) for every subsequent next request. You can
set :attr:`Site.keep_erroneous_cache_files` to `True` if you need to see the
partly generated cache file.  **Don't forget to remove this** when you have
inspected the file and fixed the reason of the exception, because if this is
`True` and some next exception occurs (which will happen sooner or later), then
all subsequent requests will usually end up to the user with a blank screen and
(if they notice it), a message :message:`TypeError: Lino.main_menu is undefined`
in their JavaScript console.
