from rest_framework.serializers import Serializer
from rest_framework.serializers import ListField, CharField, IntegerField


class ProductSerializer(Serializer):
    product = IntegerField()
    quantity = IntegerField()


class OrderSerializer(Serializer):
    products = ListField(
        child=ProductSerializer(),
        allow_empty=False,
        write_only=True
    )
    firstname = CharField()
    lastname = CharField()
    phonenumber = CharField()
    address = CharField()
