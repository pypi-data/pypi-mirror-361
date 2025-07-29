====================================
Why Lino doesn't use ManyToManyField
====================================

The ManyToManyField is an anti-feature.

Here is a classical use case::

  class Topic(Model):
    name = CharField()

  class Person(Model):
    topics = ManyToManyField(Topic)

We have persons and topics, and we want to say things like
"Person X is interested in topics Y and Z"
and
"Person Foo is interested in topics Bar"

Django creates an automatic invisible table "PersonTopic" to store each
"checked" topic on a person.

https://docs.djangoproject.com/en/5.0/topics/db/examples/many_to_many/

Usually it happens that you must extend an m2m field using the  `through
<https://docs.djangoproject.com/en/5.0/ref/models/fields/#django.db.models.ManyToManyField.through>`__ keyword.

In Lino we prefer to say::

  class Topic(dd.Model):
    name = CharField()

  class Person(dd.Human):
    topics = ManyToManyField(Topic)

  class Interest(dd.Model):
    topic = ForeignKey(Topic, related_name="interests_by_topic")
    person = ForeignKey(Person, related_name="interests_by_person")

  class InterestsByPerson(dd.Table):
    model = "Interest"
    master_key = "person"

  class InterestsByTopic(dd.Table):
    model = "Interest"
    master_key = "topic"

  class Persons(dd.Table):
    detail_layout = """
    first_name last_name
    InterestsByPerson
    """




class Product

 specs = m2mfield(Spec)


class ProductSpec:
  product = ForeignKey(Product)
  spec = ForeignKey(Spec)



SpecsByProduct(Table):
  model  = "ProductSpec"
  master_key = 'product'
  insert_layout = """
  spec
  spec__name
  """

 UsagesBySpecs(Table):
  model  = "ProductSpec"
  master_key = 'spec'

ProductDetail = """
SpecsByProduct
"""
