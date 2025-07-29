===============
Lino and Django
===============

The differences between Lino and plain Django are visible mainly for
the application developer.

(:count:`step`) A first an most visible difference with plain Django projects is
that your Lino applications have an out-of-the box :term:`front end`.  You don't
not need to write any views, URLconf, HTML, CSS nor JavaScript.

But Lino is more than a front end. Here are the **under the hood** differences
between Lino and Django.

(:count:`step`) Lino adds the concept of an central :doc:`application object
</dev/application>` while Django is a radically decentralized approach. We
believe that without such a central place it is not possible -or at least not
efficient- to maintain complex software projects.

(:count:`step`) Lino is a replacement for `Django's admin interface
<https://docs.djangoproject.com/en/5.0/ref/contrib/admin>`__ which has obviously
not been designed as a base for writing and maintaining collections of reusable
customized database applications.

(:count:`step`) Lino replaces Django's database-stored user groups and
permissions system by a system that uses pure Python code objects. This approach
is more suitable for defining and maintaining complex applications.

(:count:`step`) Lino doesn't use `django.forms
<https://docs.djangoproject.com/en/5.0/ref/forms/>`__ because they aren't
needed.  We believe that the django.forms API is "somehow hooked into the wrong
place" and forces application developers to write redundant code. Lino replaces
Django's forms by the concept of :doc:`layouts </dev/layouts/index>`.


(:count:`step`) In Django, "one typical workflow in creating Django apps is to
create models and get the admin sites up and running as fast as possible, so
your staff (or clients) can start populating data. Then, develop the way data is
presented to the public." (`source
<https://docs.djangoproject.com/en/5.0/intro/overview/>`__) Lino makes the
result of this development step *reusable*. Rather than letting your staff or
clients populate data by hand, you write :term:`demo fixtures` based on  samples
of existing data. During the early development phase this is more efficient than
letting end users enter data by hand. They will play on real data as soon as you
and your client agree that it's time to let them play on real data.

(:count:`step`) Lino suggests its own system for :doc:`database migrations
</dev/datamig>` instead of Django's default `Migrations
<https://docs.djangoproject.com/en/5.0/topics/migrations/>`_ system.

(:count:`step`) Lino prefers Jinja2 templates over the `default Django engine
<https://docs.djangoproject.com/en/5.0/topics/templates/>`_ to generate its own
stuff.  For the plain Django part of your application you can use the system of
your choice.

(:count:`step`) Lino adds concepts like actions, choosers, choicelists,
workflows, multi-lingual database content, generating printable documents, ...

(:count:`step`) Lino comes with a set of high level features like
:mod:`lino.modlib.comments`, :mod:`lino.modlib.changes`,
:mod:`lino_xl.lib.excerpts`, :mod:`lino.modlib.summaries`, ...
