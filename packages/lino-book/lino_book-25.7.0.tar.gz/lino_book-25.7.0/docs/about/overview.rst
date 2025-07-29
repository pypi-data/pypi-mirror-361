.. _dev.overview:

==================================
Repositories of the Lino framework
==================================

.. contents::
   :depth: 1
   :local:


.. _dev.overview.diagram:

Overview diagram
================

.. graphviz::

   digraph foo {

    { rank = same;
        # applications;
        noi;
        cosi;
        tera;
        voga;
        avanti;
        weleup;
        welcht;
        amici;
    }

    xl -> lino;
    noi -> xl;
    cosi -> xl;
    tera -> xl;
    avanti -> xl;
    voga -> xl;
    amici -> xl;
    weleup -> welfare;
    welcht -> welfare;

    # book -> noi;
    # book -> cosi;
    # book -> voga;
    # book -> tera;
    # book -> avanti;
    # book -> weleup;
    # book -> welcht;

    welfare -> xl;

   }


Until 2021 our :term:`repositories <code repository>` were hosted on `GitHub
<https://github.com/lino-framework>`__. In March 2021 we started to move to
`GitLab <https://gitlab.com/lino-framework>`__. Check :doc:`/team/gh2gl` when in
doubt whether your clone is up to date.



General framework repositories
==============================

.. _lino:

The ``lino`` package
--------------------

The :mod:`lino` package contains the core of the framework and includes the
:doc:`/specs/modlib`, a :term:`plugin library` with basic features like system
users, notifications, comments, printing and others. These features are
included in most real-world :term:`Lino applications <Lino application>`.

Project homepage: https://gitlab.com/lino-framework/lino

.. _xl:

Lino Extensions Library
-----------------------

The :mod:`lino_xl` package contains the :term:`Lino Extensions Library`.

Project homepage: https://github.com/lino-framework/xl

Application repositories
========================

Each Lino application has its own repository.
See :ref:`getlino.apps`.

We differentiate between "stand-alone" and "privileged" apps. See :ref:`lino.apps`.

Documentation repositories
==========================

These repositories contain mostly :file:`.rst` source code files used to
generate documentation.

.. _lf:

Main website
------------

Project homepage: https://gitlab.com/lino-framework/lf

Published at: https://www.lino-framework.org

.. _cg:

Community Guide
---------------

Project homepage: https://gitlab.com/lino-framework/cg

Published at: https://community.lino-framework.org

.. _ug:

User Guide
------------

Project homepage: https://gitlab.com/lino-framework/ug

Published at: https://using.lino-framework.org

.. _hg:

Hosting Guide
-------------

Project homepage: https://gitlab.com/lino-framework/hg

Published at: https://hosting.lino-framework.org

.. _book:

Developer Guide
--------------------

This repository contains the :term:`source code` of the :term:`Developer Guide`
(which you are reading right now), a collection of :term:`demo projects <demo
project>` (in :mod:`lino_book.projects`), and the main :term:`test suite` for
the Lino framework.

Project homepage: https://gitlab.com/lino-framework/book

Published at: https://dev.lino-framework.org


Alternative front ends
======================

See also :ref:`ug.front_ends`.

.. _react:

React front end
---------------

See https://gitlab.com/lino-framework/react

.. _extjs6:

ExtJS 6 front end
-----------------

A proof of concept for a Lino :term:`front end` that uses Sencha's ExtJS 6
JavaScript toolkit.

See https://github.com/lino-framework/extjs6

.. _openui5:

OpenUI5 front end
-----------------

A proof of concept for a Lino :term:`front end` that uses SAP's OpenUI toolkit.

See https://github.com/lino-framework/openui5


.. _pyqt:

PyQt front end
--------------

A proof of concept for a Lino :term:`front end` that uses the `PyQt toolkit
<https://en.wikipedia.org/wiki/PyQt>`__.

You can see it by saying :cmd:`pm qtclient` in the :term:`project directory
<Django project directory>` of any :term:`demo project`
(after having said :cmd:`pip install PyQt5`).



Utilities maintained by the Synodalsoft team
============================================

Some packages that might be useful to non-Lino Python projects are not covered
in the Lino Book because they are actually not at all related to Lino, except
that Lino depends on them and that they are maintained by the Lino team:

- :mod:`synodal` : :doc:`/specs/synodal/index`

- :mod:`getlino` is the Lino installer. :doc:`/specs/synodal/index`

- :mod:`atelier` is a minimalist "development framework", including a project
  management a suite of invoke commands and a set of Sphinx extensions.

- :mod:`rstgen` is a library to generate reSTructuredText snippets.

- :mod:`etgen` is used for generating HTML or XML via ElementTree.


.. _eidreader:

eidreader
---------

See https://eidreader.lino-framework.org/

See also :ref:`eidreader.java`.



.. _commondata:

commondata
----------

- https://github.com/lsaffre/commondata
