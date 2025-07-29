from lino.api import dd, rt


def objects():
    User = rt.models.users.User
    yield User(username='jvdbrug',
               first_name='Jan',
               last_name='Van den Brug',
               email='jan@dupond.be')

    yield User(username='jdupond',
               first_name='Jean',
               last_name='Dupond',
               email='jean@dupond.be')
