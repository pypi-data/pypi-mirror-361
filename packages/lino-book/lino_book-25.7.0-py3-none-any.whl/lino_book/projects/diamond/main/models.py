from django.db import models


class Addressable(models.Model):

    class Meta:
        abstract = True

    street = models.CharField(max_length=255)


class Restaurant(Addressable):
    name = models.CharField(max_length=255)


class Bar(Restaurant):
    bar_restaurant = models.OneToOneField(Restaurant,
                                          parent_link=True,
                                          on_delete=models.CASCADE)
    min_age = models.IntegerField()


class Pizzeria(Restaurant):
    pizzeria_restaurant = models.OneToOneField(Restaurant,
                                               parent_link=True,
                                               on_delete=models.CASCADE)
    specialty = models.CharField(max_length=255)


class PizzaBar(Bar, Pizzeria):
    pizza_bar_specific_field = models.CharField(max_length=255)
