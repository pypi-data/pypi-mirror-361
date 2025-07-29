.. _writedocs.shared:

==========================
Shared documentation pages
==========================

Shared Sphinx source files
==========================

Some Lino doctrees contain *shared Sphinx source files*. The master copies of
these files are maintained by convention in the `book` repository. Other
repositories act as slaves of the book: they copy these files from the book when
you run :cmd:`inv bd` in these repositories.

The :envvar:`make_docs_command` of a slave repository is set to
``'./make_docs.sh'``, and the repository has a script of that name in its root
directory.

.. xfile:: make_docs.sh

Update shared source files from the master to the slave.

The content of this script is the same for most slaves::

  #!/bin/bash
  set -e

  BOOK=../book/docs
  if [ -d $BOOK ] ; then
    cp -au $BOOK/shared docs/
    cp -au $BOOK/copyright.rst docs/
  fi

But for example in the `lf` repository it additionally runs :cmd:`getlino list
--rst` to generate the `docs/apps.rst` file (:ref:`getlino.apps`).

Keep in mind that the :xfile:`make_docs.sh` file will also be invoked on GitLab
where the book repository is not present.

Shared include files
====================

The following files are meant to be included by other files using the
:rst:dir:`include` directive.

.. xfile:: docs/shared/include/defs.rst
.. xfile:: docs/shared/include/tested.rst
