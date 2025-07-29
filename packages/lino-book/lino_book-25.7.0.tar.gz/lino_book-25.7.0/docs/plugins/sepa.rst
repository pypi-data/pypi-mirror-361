=================================================
``sepa`` : Communicating with the bank using SEPA
=================================================

.. currentmodule:: lino_xl.lib.sepa

The :mod:`lino_xl.lib.sepa` plugin adds functionality for managing bank accounts
for your partners.  When this plugin is installed, every partner can have one or
several bank accounts.

The name ``sepa`` is actually irritating because this plugin won't do any
:term:`SEPA` transfer. Maybe rename it to ``iban``? OTOH it is needed by the
actual SEPA modules :mod:`lino_xl.lib.b2c` and :mod:`lino_cosi.lib.c2b`.

It requires the :mod:`lino_xl.lib.accounting` plugin.

.. glossary::

  SEPA

    Single Euro Payments Area, a payment integration initiative of the European
    Union for simplification of bank transfers denominated in euros (`Wikipedia
    <https://en.wikipedia.org/wiki/Single_Euro_Payments_Area>`__).




.. class:: Account

    A bank account related to a given :term:`partner`.

    .. attribute:: partner

      The :term:`partner` who owns this bank account.

    .. attribute:: iban

      IBANField(verbose_name=_("IBAN"))

    .. attribute:: bic

      BICField(verbose_name=_("BIC"), blank=True)

    .. attribute:: remark

      CharField(_("Remark"), max_length=200, blank=True)

    .. attribute:: primary

      Whether this is the primary bank account of this partner.

    .. attribute:: statements

        A virtual field which displays the date of the last imported
        statement for this account. Clicking on this date will open
        the `B2C account <lino_xl.lib.b2c.models.Account>` with same
        IBAN number.

        This field is empty when no B2C Account exists.

        Available only when :mod:`lino_xl.lib.b2c` is installed as
        well.


.. class:: Accounts

.. class:: AccountsByPartner

    Shows the bank account(s) known for the given partner.


.. class:: BankAccount

    Defines a field :attr:`bank_account` and its chooser.
