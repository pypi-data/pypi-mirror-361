import factory


class OrderableFactory(factory.django.DjangoModelFactory):
    class Meta:
        abstract = True

    sort_order = factory.Sequence(lambda n: n)
