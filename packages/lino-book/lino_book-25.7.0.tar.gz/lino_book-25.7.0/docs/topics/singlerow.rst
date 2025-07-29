=================
Single-row tables
=================

A **single-row table** is a table that has only one row and hence does not need
any navigation or any other :term:`display mode` than detail. Examples:

- The `My settings` form (:class:`lino.modlib.users.Me`)
- The `Site config` form (:class:`lino.modlib.system.SiteConfigs`)
- The `My invoicing plan` of the :mod:`lino_xl.lib.invoicing` plugin
- The `Accounting report` of the :mod:`lino_xl.lib.sheets` plugin

These are implemented using the :attr:`default_record_id
<lino.core.actors.Actor.default_record_id>` attribute.
