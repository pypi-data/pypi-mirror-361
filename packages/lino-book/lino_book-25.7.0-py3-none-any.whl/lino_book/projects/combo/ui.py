from lino.api import dd


class Persons(dd.Table):
    model = 'combo.Person'
    detail_layout = dd.DetailLayout("""
    name
    country
    city
    """, window_size=(50, 'auto'))

    insert_layout = """
    name
    country
    city
    """


class Cities(dd.Table):
    model = 'combo.City'


class Countries(dd.Table):
    model = 'combo.Country'
