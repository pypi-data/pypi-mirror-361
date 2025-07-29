# This file is not used by pytest (because it contains no function starting with
# "test"). See pytest.ini instead

# from atelier.test import make_docs_suite
#
# do_not_test = [
#     "docs/dev/lets/step4.rst",
#     "docs/apps/noi/mailbox.rst",
#     "docs/apps/noi/github.rst",
#     "docs/plugins/ibanity.rst",
#     "docs/apps/noi/ibanity.rst",
#     "docs/apps/cosi/ibanity.rst",
# ]
#
# def load_tests(loader, standard_tests, pattern):
#     suite = make_docs_suite(
#         "docs",
#         addenv=dict(LINO_LOGLEVEL="INFO"),
#         exclude=do_not_test
#     )
#     return suite
