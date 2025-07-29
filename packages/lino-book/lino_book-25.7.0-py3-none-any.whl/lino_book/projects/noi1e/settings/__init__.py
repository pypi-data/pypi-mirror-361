# -*- coding: UTF-8 -*-
# Copyright 2014-2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

# from pathlib import Path
from lino.core.auth.utils import activate_social_auth_testing
from lino_noi.lib.noi.settings import *

try:
    from lino_local.settings import *
except ImportError:
    pass


class Site(Site):

    workflows_module = 'lino_book.projects.noi1e.workflows'

    is_demo_site = True
    the_demo_date = 20150522
    # the_demo_date = 20250328
    # must not be a weekend otherwise nobody is working in the demo data

    languages = "en de fr"
    # readonly = True
    catch_layout_exceptions = False
    default_build_method = 'weasy2pdf'

    # use_elasticsearch = True
    # use_solr = True
    # use_linod = True
    # use_ipdict = True
    use_experimental_features = True

    # default_ui = 'lino_extjs6.extjs6'
    # default_ui = 'lino.modlib.bootstrap3'
    # default_ui = 'lino_openui5.openui5'
    # default_ui = 'lino_react.react'

    # def get_installed_plugins(self):
    #     yield super(Site, self).get_installed_plugins()
    #     yield 'lino_react.react'

    def get_plugin_configs(self):
        yield super().get_plugin_configs()
        yield 'excerpts', 'responsible_user', 'jean'
        yield 'notify', 'use_push_api', True
        # email: noi1euser@gmail.com ; password: dAb4V8h6WpzinJe
        # yield 'google', 'client_secret_file', Path(__file__).parent / 'google_creds.json'
        yield 'users', 'third_party_authentication', True
        # yield 'vat', 'declaration_plugin', 'lino_xl.lib.eevat'
        # yield "peppol", "simulate_endpoints", True

    def get_installed_plugins(self):
        # add lino.modlib.restful to the std list of plugins
        yield super().get_installed_plugins()
        yield 'lino.modlib.restful'
        yield 'lino_xl.lib.google'
        yield 'lino.modlib.search'
        # yield 'lino_xl.lib.caldav'
        # 20210305 removed mailbox. See :mod:`lino_xl.lib.mailbox`.
        # 20231217 tried to use it again after https://github.com/coddingtonbear/django-mailbox/issues/150
        # But it still gives AttributeError: type object 'Message' has no attribute 'collect_virtual_fields'
        # yield 'lino_xl.lib.mailbox'

    def setup_plugins(self):
        """Change the default value of certain plugin settings.

        - :attr:`excerpts.responsible_user
          <lino_xl.lib.excerpts.Plugin.responsible_user>` is set to
          ``'jean'`` who is both senior developer and site admin in
          the demo database.

        """
        super(Site, self).setup_plugins()
        # self.plugins.social_auth.configure(
        #     backends=['social_core.backends.github.GithubOAuth2'])
        # self.plugins.excerpts.configure(responsible_user='jean')
        if self.is_installed('extjs'):
            self.plugins.extjs.configure(enter_submits_form=False)
        if False:
            self.plugins.mailbox.add_mailbox(
                'mbox', "Luc's aaa mailbox",
                '/home/luc/.thunderbird/luc/Mail/Local Folders/aaa')


DEBUG = True
ALLOWED_HOSTS = ["*"]


# Have google plugin installed. Use the settings from google plugin and hence: `google=False`
activate_social_auth_testing(globals(), google=False)

if False:  # not needed for newbies

    # Add ldap authentication. Requires  Hamza's fork of django_auth_ldap.
    # temporary installation instructions:
    # $ sudo apt-get install build-essential python3-dev python2.7-dev libldap2-dev libsasl2-dev slapd ldap-utils lcov valgrind
    # $ pip install -e git+https://github.com/khchine5/django-auth-ldap.git#egg=django-auth-ldap
    # import ldap
    # from django_auth_ldap.config import LDAPSearch, LDAPGroupType,GroupOfNamesType,LDAPSearchUnion,GroupOfUniqueNamesType

    AUTHENTICATION_BACKENDS.append("django_auth_ldap.backend.LDAPBackend")

    AUTH_LDAP_SERVER_URI = "ldap://ldap.forumsys.com"
    AUTH_LDAP_USER_DN_TEMPLATE = "uid=%(user)s,dc=example,dc=com"
    AUTH_LDAP_USER_ATTR_MAP = {
        'first_name': 'givenName',
        'last_name': 'sn',
        'email': 'mail',
    }
