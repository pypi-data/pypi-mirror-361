.. _polly.intro:

==========================
Introduction to Lino Polly
==========================

Lino Polly is a general-purpose web application to manage polls.
A **poll** is a series of questions to be asked to a number of people.
A **response** is when somebody answers to a poll.

- To see :ref:`polly` follow the instructions in :doc:`/discover`

- Create new polls : :menuselection:`Polls --> Polls`

- Create your response to a poll : :menuselection:`Polls --> My responses`

- Create more "choice sets" in
  :menuselection:`Configuration -- > Polls --> ChoiceSets`
  (a choice set is a reusable set of possible answers to a question.
  Polly currently supports only blueprint questions with reusable sets of
  answers.)

TODO:

- More useful information in the `Results` tab
- Display pending polls on the welcome page
- Printable result sheet
- Workflow & user permissions

- Cannot define multiple choice questions.
  To remain 3NF, this requires another table
