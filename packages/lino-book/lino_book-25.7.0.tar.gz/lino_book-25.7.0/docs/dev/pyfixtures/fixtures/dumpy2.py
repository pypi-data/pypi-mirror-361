from lino.utils.instantiator import Instantiator

User = Instantiator('users.User', 'username first_name last_name email').build


def objects():
    yield User('jvdbrug', 'Jan', 'Van den Brug', 'jan@dupond.be')
    yield User('jdupond', 'Jean', 'Dupond', 'jean@bommel.be')
