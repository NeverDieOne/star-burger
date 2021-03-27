from django.db import models
from django.db.models import Sum
from django.core.validators import MinValueValidator
from django.utils import timezone

from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField('название', max_length=50)
    address = models.CharField('адрес', max_length=100, blank=True)
    contact_phone = models.CharField('контактный телефон', max_length=50, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'


class ProductQuerySet(models.QuerySet):
    def available(self):
        return self.distinct().filter(menu_items__availability=True)


class ProductCategory(models.Model):
    name = models.CharField('название', max_length=50)

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField('название', max_length=50)
    category = models.ForeignKey(ProductCategory, null=True, blank=True, on_delete=models.SET_NULL,
                                 verbose_name='категория', related_name='products')
    price = models.DecimalField('цена', max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    image = models.ImageField('картинка')
    special_status = models.BooleanField('спец.предложение', default=False, db_index=True)
    description = models.TextField('описание', max_length=200, blank=True)

    objects = ProductQuerySet.as_manager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items',
                                   verbose_name="ресторан")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='menu_items',
                                verbose_name='продукт')
    availability = models.BooleanField('в продаже', default=True, db_index=True)

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]


class OrderQuerySet(models.QuerySet):
    def fetch_with_total_price(self):
        return self.annotate(
            total_price=Sum(
                'order_items__price',
                output_field=models.DecimalField()
            ),
        )

class Order(models.Model):
    UNPROCESSED = 'Unproc'
    PROCESSED = 'Proc'
    CASH = 'Cash'
    ELECTRONIC = 'Electro'

    STATUSES = [
        (UNPROCESSED, 'Необработанный'),
        (PROCESSED, 'Обработанный')
    ]

    PAYMENTS = [
        (CASH, 'Наличными'),
        (ELECTRONIC, 'По карте')
    ]

    firstname = models.CharField('Имя', max_length=20, db_index=True)
    lastname = models.CharField('Фамилия', max_length=20, db_index=True)
    phonenumber = PhoneNumberField('Номер телефона', db_index=True)
    address = models.CharField('Адрес', max_length=255, db_index=True)
    status = models.CharField('Статус заказа', choices=STATUSES, default=UNPROCESSED, max_length=6, db_index=True)
    payment = models.CharField('Метод оплаты', choices=PAYMENTS, default=CASH, max_length=7, db_index=True)

    comment = models.TextField('Комментарий', blank=True)

    registered_at = models.DateTimeField('Время заказа', default=timezone.now, db_index=True)
    called_at = models.DateTimeField('Время звонка', blank=True, null=True, db_index=True)
    delivered_at = models.DateTimeField('Время доставки', blank=True, null=True, db_index=True)

    objects = OrderQuerySet.as_manager()

    def __str__(self):
        return f'{self.phonenumber} - {self.address}'

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class OrderItem(models.Model):
    quantity = models.IntegerField('Количество')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items', verbose_name='Продукт')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items', verbose_name='Заказ')
    price = models.DecimalField('Цена', decimal_places=2, max_digits=8, validators=[MinValueValidator(0)])

    def __str__(self):
        return f'{self.product.name}: {self.quantity}'
