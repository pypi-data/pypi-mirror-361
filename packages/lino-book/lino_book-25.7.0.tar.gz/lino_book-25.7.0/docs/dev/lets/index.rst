.. _dev.lets:
.. _lino.tutorial.lets:

=============================
The LETS tutorial
=============================

..
  In this tutorial we imagine a whole Lino project, from analysis to deployment,
  testing and documentation.

..
  More about the Lino application development process
  in :doc:`/dev/analysis`.

In this tutorial we are going to explore a fictive application to run a `Local
Exchange Trade System
<https://en.wikipedia.org/wiki/Local_exchange_trading_system>`_ (LETS). The users
of that site would register the products and services they want to sell or to
buy. The goal is to connect the "providers" and the "customers". We don't care
whether and how transactions actually occur, neither about history... we just
help them to find each other.

The application described here is probably a bit too simple for a real-life
website, but we *imagine* that this is what our customer *asked* us to do.


.. toctree::
    :maxdepth: 2

    1

.. toctree::
    :hidden:

    step1
    step2
    step3
    step4
    m2m
    docs

Planned next steps:

- adding actions
- social auth
- uploading images
- i18n
- comments
- switching between ExtJS and React
- publisher
