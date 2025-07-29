.. module:: synodal

========================================
``synodal`` : Metadata about Synodalsoft
========================================

The ``synodal`` package contains metadata about the code repositories maintained
by the `Synodalsoft project <https://www.synodalsoft.net>`__.

It is used for example by :ref:`getlino` to clone and install the Synodalsoft
packages, and by :func:`lino.sphinxcontrib.configure` to set
:envvar:`intersphinx_mapping`.

Source code repository: https://gitlab.com/lino-framework/synodal

Change history: https://gitlab.com/lino-framework/synodal/-/commits/master


Instructions for the maintainer
===============================

The :xfile:`synodal.py` file is generated code. You generate it by running the
:xfile:`make_code.py` file::

  ./make_code.py

You need a full :term:`developer environment` installed in order to do this.

The distributed package contains only the :xfile:`synodal.py` file, not the
:xfile:`make_code.py` file.

Run :cmd:`inv test` before publishing.

How to release to :term:`PyPI`: see :doc:`/dev/release`.
