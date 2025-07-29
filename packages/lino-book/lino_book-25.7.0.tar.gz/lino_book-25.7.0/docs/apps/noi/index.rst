.. _noi.specs:

========================
Lino Noi Developer Guide
========================

This is the developer documentation for :ref:`noi`.

.. toctree::
    :maxdepth: 1
    :glob:

    general
    tour/index
    db
    watch

Plugins in Noi
===================

.. toctree::
    :maxdepth: 1
    :glob:

    tickets
    comments
    memo
    invoicing
    groups
    cal
    storage
    users


The Noi ``workflows_module``
============================

.. currentmodule:: lino_noi.lib.noi

.. module:: lino_noi.lib.noi.workflows

The default :attr:`workflows_module
<lino.core.site.Site.workflows_module>` for :ref:`noi` applications.

This workflow requires that both :mod:`lino_xl.lib.tickets` and
:mod:`lino_xl.lib.votes` are installed.


Don't read me
=============

.. toctree::
    :maxdepth: 1
    :glob:

    as_pdf
    std
    public
    bs3
    ddh
    export_excel
    sql
    suggesters
    api
    mailbox
    faculties
    votes
    github
    stars
