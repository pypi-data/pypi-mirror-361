from lino.api import dd


class Food(dd.Model):

    class Meta:
        abstract = True

    type = dd.CharField(max_length=30)


class Vegetable(Food):

    class Meta:
        abstract = True

    color = dd.CharField(max_length=30)


class Potato(Vegetable, Food):
    weight = dd.IntegerField()
