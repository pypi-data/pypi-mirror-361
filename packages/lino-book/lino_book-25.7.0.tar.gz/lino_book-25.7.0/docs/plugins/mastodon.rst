.. doctest docs/plugins/mastodon.rst
.. _dg.plugins.mastodon:

==================
``mastodon`` OAuth
==================

.. module:: lino_xl.lib.mastodon

.. currentmodule:: lino_xl.lib.mastodon

Python Social Auth (PSA) does NOT yet provide authentication method for mastodon.
We subclass the `BaseOAuth2` from `social_core` and put necessary attributes on it
so that :class:`MastodonOAuth2` becomes our backend for mastodon authentication.

.. class:: MastodonOAuth2

    The backend for mastodon OAuth authentication methods.

The original idea was to have API methods communicating with mastodon app on designed
action call(s), publishing the results of some bulk action on mastodon, so that, the
users may get a notification on mastodon. We decided to abandon this idea.
