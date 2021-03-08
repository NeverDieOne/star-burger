import json
from django.db.models.fields.related import OneToOneField

from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Product
from .models import Order, OrderItem


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            },
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    data = request.data

    if not validate_order(data):
        return Response({'Error': 'Validate error'}, status=status.HTTP_400_BAD_REQUEST)
    
    order = Order.objects.create(
        first_name=data['firstname'],
        last_name=data['lastname'],
        phone_number=data['phonenumber'],
        address=data['address']
    )

    for product in data['products']:
        OrderItem.objects.create(
            order=order,
            product=Product.objects.get(id=product['product']),
            quantity=product['quantity']
        )

    return Response(data)


def validate_order(order):
    products = order.get('products')
    first_name = order.get('firstname')
    last_name = order.get('lastname')
    address = order.get('address')
    phone_number = order.get('phonenumber')

    if any([
        not isinstance(products, list),
        not isinstance(first_name, str),
        not isinstance(last_name, str),
        not isinstance(address, str),
        not isinstance(phone_number, str),
        not products,
        not first_name,
        not last_name,
        not address,
        not phone_number,
    ]):
        return False

    for product in products:
        product_id = product['product']

        if not isinstance(product_id, int) or not Product.objects.filter(id=product_id):
            return False
    
    return True
