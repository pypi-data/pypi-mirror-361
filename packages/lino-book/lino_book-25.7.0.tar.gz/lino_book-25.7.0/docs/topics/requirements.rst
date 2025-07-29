==================
About requirements
==================

The Python packaging system has an established mechanism for specifying
dependencies, i.e. other Python packages that are required to run your package.

Lino uses this system. When you distribute a  :term:`Lino application` or
:term:`plugin library`, you specify required packages in your
:xfile:`setup_info.py` file.

But what it a third-party Python package is required only under certain
conditions? Plugins can have quite sophisticated logic to decide which packages
they require. For example, a production site needs :mod:`atelier` only if it
actually generates local help pages, i.e. when the application uses the
:mod:`lino.modlib.help` plugin and :setting:`help.make_help_pages` is set to
`True`.

That's why we have the :meth:`lino.core.plugin.Plugin.get_requirements` method.

Keep in mind that packages specified using :meth:`get_requirements` will get
installed only in a second step. So when you import them from your plugin, you
need to wrap them into a ``try ... except ImportError``.
