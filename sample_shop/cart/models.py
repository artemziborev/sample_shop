from functools import reduce

from django.db import models
from django.utils.timezone import get_default_timezone
from model_utils.models import TimeStampedModel
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from sample_shop.orders.models import AbstractItem
tz = get_default_timezone()

from . import emails as cart_email

# class Order(TimeStampedModel):
#     completed = models.BooleanField(_('Оформленный заказ'), default=False)
#     name = models.CharField(_('Имя'), max_length=100, default='')
#     email = models.EmailField(_('Email'), default='')
#     phone = models.CharField(_('Телефон'), max_length=30, default='')
#     city = models.CharField(_('Город'), max_length=100, default='', blank=True)
#     comment = models.TextField(_('Комментарий'), default='', blank=True)
#     layout = models.FileField(_('Макет'), upload_to='layout', blank=True, default='')
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name='orders',
#         blank=True,
#         null=True,
#         verbose_name=_('Пользователь'),
#     )
#
#     class Meta:
#         verbose_name = _('Заказ')
#         verbose_name_plural = _('Заказы')
#         ordering = ['-created']
#
#     def __str__(self):
#         return _('Заказ от {}').format(self.created.astimezone(tz).strftime('%d.%m.%Y %H:%M'))

class CartAssemblyRequest(models.Model):
    STATUS_PROCESSING = 0
    STATUS_ASSEMBLED = 1
    STATUS_REJECTED_BY_SHOP = 2
    STATUSES_CHOICES = (
        (STATUS_PROCESSING, _('В обработке')),
        (STATUS_ASSEMBLED, _('Собран')),
        (STATUS_REJECTED_BY_SHOP, _('Отклонен магазином')),
    )

    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата изменения'), auto_now=True)
    file = models.FileField(_('Счёт'), upload_to='cart_assembly_requests/%Y/%m/%d', default='', blank=True)
    status = models.PositiveIntegerField(_('Статус'), choices=STATUSES_CHOICES, default=STATUS_PROCESSING)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assemblies', verbose_name=_('Пользователь')
    )

    accepted = models.BooleanField(_('Assembled'), default=False)
    accepted_complete = models.BooleanField(default=False)
    accepted_message = models.TextField(_('Message Text'), default='', blank=True)

    rejected = models.BooleanField(_('Rejected'), default=False)
    rejected_complete = models.BooleanField(default=False)
    rejected_message = models.TextField(_('Причина отказа'), default='', blank=True)

    class Meta:
        verbose_name = _('Shopping Cart Assembly Request')
        verbose_name_plural = _('Заявки на сбор корзины')

    def __str__(self):
        return "%s %s" % (self.user.email, self.created_at.astimezone(tz).strftime('%d.%m.%Y %H:%M'))

    def send_email(self):
        email = cart_email.CartAssemblyRequestEMail(self)
        return email.send()

    def send_manager_email(self):
        email = cart_email.CartAssemblyRequestManagerEmail(self)
        return email.send()

    def send_accepted_email(self):
        email = cart_email.CartAssemblyRequestAcceptedEmail(self)
        return email.send()

    def send_rejected_email(self):
        email = cart_email.CartAssemblyRequestRejectedEmail(self)
        email.send()

    @property
    def comment(self):
        return "; ".join(["%s - %s" % (item.article, item.comment) for item in self.items.exclude(comment="")])

    @property
    def total_price(self):
        return reduce(lambda a, c: a + c.total_price, self.items.all(), 0)


class CartAssemblyRequestItem(AbstractItem):
    assembly = models.ForeignKey(CartAssemblyRequest, on_delete=models.CASCADE, related_name='items')
    auto_url = models.CharField(_('Ссылка на страницу'), max_length=250, default='', blank=True)


class CartAssemblyRequestFile(models.Model):
    assembly = models.ForeignKey(
        CartAssemblyRequest, on_delete=models.CASCADE, related_name='files', null=True, verbose_name=_('Заявка на сбор')
    )
    file = models.FileField(_('Файл'), upload_to='cart_assembly_request_file', default='')

    class Meta:
        verbose_name = _('Приложенный файл')
        verbose_name_plural = _('Приложенные файлы')
