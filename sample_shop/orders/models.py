from decimal import Decimal
from functools import reduce

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db import models
from . import email as cart_email

User = get_user_model()

class AbstractItem(models.Model):
    article = models.CharField(_('Артикул товара'), max_length=255, default='')
    name = models.CharField(_('Имя товара'), max_length=255, default='')
    price = models.DecimalField(_('Цена за единицу'), max_digits=10, decimal_places=2, default=Decimal('0.00'))
    min_price = models.DecimalField(
        _('Минимальная цена за единицу'), max_digits=10, decimal_places=2, default=0, blank=True
    )
    count = models.PositiveIntegerField(_('Количество'), default=1, blank=True)
    comment = models.CharField(_('Комментарий к товару'), max_length=250, blank=True, default='')
    is_promo = models.BooleanField(_('Промо товар'), default=False)

    class Meta:
        abstract = True

    @property
    def total_price(self):
        price = self.price
        if self.is_promo and self.min_price:
            price = self.min_price
        return price * self.count



class Order(models.Model):
    STATUS_CREATED = 1
    STATUS_PROCESSING = 2
    STATUS_UNPROCESSED = 3
    STATUS_ASSEMBLED = 4
    STATUS_CONFIRMED_OR_RESERVED = 5
    STATUS_CLOSED = 6
    STATUS_PAID = 7
    STATUSES_CHOICES = (
        (STATUS_CREATED, _('Заказ создан')),
        (STATUS_PROCESSING, _('На согласовании')),
        (STATUS_UNPROCESSED, _('Не оплачен')),
        (STATUS_ASSEMBLED, _('К отгрузке')),
        (STATUS_CONFIRMED_OR_RESERVED, _('К выполнению / В резерве')),
        (STATUS_CLOSED, _('Закрыт')),
        (STATUS_PAID, _('Оплачен')),
    )

    DELIVERY_TYPE_TAKEOUT = 0
    DELIVERY_TYPE_COURIER = 1
    DELIVERY_TYPE_CHOICES = ((DELIVERY_TYPE_TAKEOUT, _('Самовывоз')), (DELIVERY_TYPE_COURIER, _('Доставка курьером')))

    PAYMENT_TYPE_ONLINE = 0
    PAYMENT_TYPE_WHEN_RECEIVED = 1
    PAYMENT_TYPE_INVOICE = 2
    PAYMENT_TYPE_CHOICES = (
        (PAYMENT_TYPE_ONLINE, _("Платежная карта")),
        (PAYMENT_TYPE_WHEN_RECEIVED, _("Наличный")),
        (PAYMENT_TYPE_INVOICE, _("Безналичный")),
    )

    order_user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name=_('Заказчик'), related_name='orders'
    )
    status = models.PositiveIntegerField(choices=STATUSES_CHOICES, default=STATUS_CREATED, verbose_name=_('Статус'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Дата изменения'))
    delivery_type = models.PositiveSmallIntegerField(
        _('Способ доставки'), choices=DELIVERY_TYPE_CHOICES, default=DELIVERY_TYPE_TAKEOUT, blank=True
    )
    delivery_address = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Адрес доставки'))
    payment_type = models.PositiveSmallIntegerField(
        _('Способ оплаты'), choices=PAYMENT_TYPE_CHOICES, default=PAYMENT_TYPE_WHEN_RECEIVED, blank=True
    )
    invoice_file = models.FileField(_('Файл со счетом на оплату'), upload_to='order_invoices', blank=True, null=True)
    online_payment_id = models.CharField(max_length=255, verbose_name=_('ID онлайн-платежа'), unique=True, blank=True, null=True)
    online_payment_confirm_date = models.DateTimeField(blank=True, null=True, verbose_name=_('Дата оплаты заказа'))
    online_payment_last_try = models.DateTimeField(_('Дата последней попытки оплаты заказа'), blank=True, null=True)
    confirmed = models.BooleanField(_('Подтвержденная оплата'), default=False)

    class Meta:
        verbose_name = _('заказ')
        verbose_name_plural = _('заказы')

    def __str__(self):
        return "Заказ от " + self.user.email + ", " + self.created_at.strftime("%d.%m.%Y")

    def get_status(self):
        web_order = WebOrder()
        return web_order.status(self.remote_id)

    def confirm_online_payment(self):
        web_order = WebOrder()
        if self.online_payment_confirm_date and not self.confirmed:
            self.send_confirm_online_payment_email()
            self.send_confirm_online_payment_client_email()
            return web_order.confirm_online_payment(
                self.remote_id,
                str(round(self.total_correct_price * 100)),
                self.online_payment_confirm_date.strftime('%Y%m%d%H%M%S'),
            )
        return False

    def send_email(self):
        email = cart_email.OrderCreatedEmail(self)
        return email.send()

    def send_manager_email(self):
        email = cart_email.OrderCreatedManagerEmail(self)
        return email.send()

    def send_confirm_online_payment_email(self):
        email = cart_email.OrderConfirmOnlinePaymentEmail(self)
        return email.send()

    def send_confirm_online_payment_client_email(self):
        '''
        посылаем клиенту письмо в подтверждением оплаты заказа
        '''
        email = cart_email.OrderConfirmOnlinePaymentClientEmail(self)
        return email.send()

    @property
    def can_download_invoice(self):
        return self.payment_type == Order.PAYMENT_TYPE_INVOICE

    @property
    def can_download_blank(self):
        return self.status != Order.STATUS_CLOSED and self.status != Order.STATUS_UNPROCESSED

    @property
    def comment(self):
        return "; ".join(
            [
                "%s - %s" % (item.article, item.comment)
                for item in self.items.filter(comment__isnull=False).exclude(comment="")
            ]
        )

    @property
    def total_price(self):
        return reduce(lambda a, c: a + c.total_price, self.items.all(), 0)

    @property
    def total_correct_price(self):
        return reduce(lambda a, c: a + c.total_correct_price, self.items.all(), 0)

    @property
    def must_be_paid_online(self):
        if self.canceled or self.validated or self.paid or self.agree_1c:
            return False
        if self.payment_type != self.PAYMENT_TYPE_ONLINE:
            return False
        # if self.online_payment_last_try is not None and (
        #     timezone.now() - self.online_payment_last_try
        # ) < timezone.timedelta(minutes=3):
        #     return False
        return self.online_payment_id is None

    @property
    def is_payment_online(self):
        return self.payment_type == Order.PAYMENT_TYPE_ONLINE

    @property
    def online_payment_timer(self):
        return self.created_at + timezone.timedelta(hours=2)

    @property
    def can_be_cancelled(self):
        return self.status != self.STATUS_CLOSED

    @property
    def canceled(self):
        return self.status == self.STATUS_CLOSED

    @property
    def created(self):
        return self.status == Order.STATUS_CREATED

    @property
    def validated(self):
        return self.status == Order.STATUS_PROCESSING

    @property
    def unpaid(self):
        return self.status == Order.STATUS_UNPROCESSED

    @property
    def paid(self):
        return self.status == Order.STATUS_PAID



class OrderItem(AbstractItem):
    order = models.ForeignKey(Order, verbose_name=_('Заказ'), related_name='order_items', on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('заказанный товар')
        verbose_name_plural = _('заказанные товары')

    def __str__(self):
        return "Заказанный товар " + self.article + " (%s)" % self.order

    @property
    def correct_price(self):
        if not self.order.user.profile.is_phys:
            return self.price
        if self.is_promo and self.min_price:
            price = self.min_price
        else:
            price = self.price
        return price

    @property
    def total_correct_price(self):
        return self.correct_price * self.count
