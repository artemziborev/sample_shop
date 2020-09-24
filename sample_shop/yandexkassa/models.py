import uuid

from django.conf import settings
from django.db import models
from model_utils.models import TimeStampedModel
from yandex_checkout import Configuration, Payment as YandexPayment, Refund

Configuration.account_id = settings.YANDEXKASSA_SHOP_ID
Configuration.secret_key = settings.YANDEXKASSA_SECRET_KEY


class Payment(TimeStampedModel):
    order = models.OneToOneField('orders.Order', on_delete=models.SET_NULL, null=True, verbose_name='Бронирование')
    cost = models.DecimalField('Размер оплаты', max_digits=9, decimal_places=2, default=0)
    status = models.CharField('Статус', max_length=255, default='', blank=True)
    inner_id = models.CharField('ID платежа', max_length=255, default='', blank=True)
    inner_key = models.UUIDField(default=uuid.uuid4, editable=False)

    class Meta:
        verbose_name = 'Платёж'
        verbose_name_plural = 'Платежи'
        ordering = ('-created',)

    def __str__(self):
        return f'{self.order if self.order else None}'

    def create_yandex_payment(self, user):
        payment_data = {
            'amount': {'value': self.cost, 'currency': 'RUB'},
            'confirmation': {'type': 'redirect', 'return_url': 'https://sample-shop.com/'},
            'capture': True,
            'description': self.__str__(),
            'receipt': {
                'customer': {'email': user.email},
                'items': [
                    {
                        'description': item.name,
                        'quantity': item.count,
                        'amount': {'value': item.price, 'currency': 'RUB'},
                        'vat_code': 1,
                    }
                    for item in self.order.items.all()
                ],
            },
        }
        return YandexPayment.create(payment_data, self.inner_key)

    def get_yandex_payment(self):
        return YandexPayment.find_one(self.inner_id)

    def create_refund(self):
        refund = Refund.create({'amount': {'value': self.cost, 'currency': 'RUB'}, 'payment_id': self.inner_id})
        if refund.status == 'succeeded':
            self.status = 'refund'
            self.save()
        return refund
