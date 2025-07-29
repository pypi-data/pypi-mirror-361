.. _team.mt:

====================
Manual testing suite
====================

.. contents::
  :local:

This document contains instructions for :term:`manually testing <manual
testing>` a series of things that aren't yet covered by any automatic test
suite.

..
  Before starting to report issues, check with your team and decide which sites
  need testing


.. _team.mt.addresses:

Multiple addresses
==================

Here are some tests for the :mod:`lino_xl.lib.addresses` plugin.

- Sign in as robin in a :ref:`amici` (e.g. :cmd:`go amici1`).

- Click on the :guilabel:`Persons` quicklink.

- Enter "dob" in the :guilabel:`Quick search` field.

- Select the first Dorothée Dobbelstein

- Hit the :kbd:`⚭` (Merge) button in the toolbar.  In the :guilabel:`into...`
  field, type "dob" and select the second Dorothée (Dobbelstein-Demeulenaere).
  Leave the other fields unchanged. Hit :kbd:`ENTER` to submit. Lino should ask
  "Are you sure you want to merge Dorothée Dobbelstein into Dorothée
  Dobbelstein-Demeulenaere? 1 Addresses, 1 List memberships will be deleted.
  Dorothée Dobbelstein will be deleted."

- Open the :term:`detail window` on Dorothée. Click on the :guilabel:`Manage
  addresses` link. Modify the `Street` field of the primary address (add "n" at
  the end). Go back to the detail view (hit :kbd:`Alt+ArrowLeft` or the
  :guilabel:`Back` button of your browser). Verify that the partner's address in
  the :attr:`overview` field has been updated correctly.

- Same as above, but mark another address as primary

- Same as above, but edit the non-primary address. The :attr:`overview` field
  should *not* change.

- Same as above, but uncheck the primary checkbox of the primary address so that
  there is no primary address. The partner's address in the :attr:`overview`
  field should become empty.

- In the grid view for Persons, make the :guilabel:`Street` column visible and
  directly edit the :guilabel:`Street` fields of a partner. The primary address
  in :guilabel:`Manage addresses` should get updated accordingly.

.. _team.mt.navigating:

Navigating on tickets
=====================

Sign in as robin on a :ref:`noi` site (e.g. :doc:`noi1r </projects/noi1r>` or
:doc:`noi1e </projects/noi1e>`.

- Click on the :guilabel:`All tickets` quicklink. The first 5 ticket numbers of
  the list are (116, 115, 114, 113, 112).

- Click on the :guilabel:`Active tickets` quicklink. The first 5 ticket
  numbers of the list are (114, 112, 111, 110, 109).

- In both lists, click on the first ticket in the list to open its detail view.

  - Hit :kbd:`PgDn` multiple times to skip to the next tickets, and check that
    Lino navigates you over the same tickets as those shown in the list (there
    have been bugs where Lino "forgot" in which of the two list it was).

  - Edit the :guilabel:`Team` field to select another team (there have been bugs
    where this caused a server error for one of these lists and not for the
    other).

Verify :ticket:`5777` (ParameterStore ... expects a list of 3 values but got 5)
===============================================================================

- Sign in as robin on a :ref:`cosi` site.

- Open the list of sales invoices

- Click on the :kbd:`↗` in front of any partner.

- Lino should display the detail of the partner.

Verify :ticket:`5751` (Invalid primary key 4968 for avanti.Clients)
===================================================================

- Sign in as robin on any :ref:`avanti` site (e.g. :doc:`avanti1
  </projects/avanti1>`)

- Select :menuselection:`Contacts --> Clients`, open the parameter panel, change
  the "State" field from  "Coached" to blank. On one of the yellow rows that
  just became visible, click the :kbd:`↗` in the first column.


Verify :ticket:`5818` (Chooser context for comboboxes in the phantom row)
=========================================================================

- Sign in as robin on :doc:`prima1 </projects/prima1>`.
- In the dashboard click on the "Science" behind "1A"
- in the "Exams of Science in 1A" panel, click on the detail arrow of first exam. Lino shows the first exam in detail view.
- Activate the "More" panel of the exam.

- In the "Challenges of test" panel, click on the "Skill" cell of the phantom
  row and expand the combobox. The combobox should show only the three skills
  defined for the Science subject, not all skills.

- When you expand the combo in an existing row of the grid, Lino correctly shows
  only the skills defined for the subject of the test.

- In the settings.py of prima1, comment out the default_ui setting and try the
  same under ExtJS where it works correctly.
