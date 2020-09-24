import re
from collections import OrderedDict

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

from . import models as cart_models
# from .logic import blank_for_order


User = get_user_model()


class OrderCreatedEmail(EmailMultiAlternatives):
    def __init__(self, order, *args, **kwargs):
        """
        """
        super().__init__(*args, **kwargs)
        user = order.user
        self.user = user
        self.order = order
        self.to = [user.email]
        self.subject = "Ваш заказ на сайте %s успешно оформлен" % settings.SITE_DOMAIN
        self.content_subtype = 'html'
        self.site_settings = models.SiteSettings.get_settings()
        self.attach_alternative(
            render_to_string(
                'emails/order.html',
                {
                    'phone': self.order.takeout_point.phone,
                    'phone_filtered': re.sub(r"[\s\-()]", "", self.order.takeout_point.phone),
                    'vk_link': self.site_settings.vk_link,
                    'site_link': "https://%s" % settings.SITE_DOMAIN,
                    'site_name': settings.SITE_DOMAIN,
                    'order': order,
                    'payment_info': order.get_payment_type_display(),
                    'client_info': {'Клиент': user.get_full_name},
                    'order_info': {
                        "Комментарий к заказу": order.comment if len(order.comment) > 0 else "Комментарий не задан"
                    },
                    'account_balance': 0,
                    'debt_amount': order.total_price,
                                    },
            ),
            'text/html',
        )



class OrderCreatedManagerEmail(EmailMultiAlternatives):
    def __init__(self, order, *args, **kwargs):
        """
        :param cart.models.Order order:
        """
        super().__init__(*args, **kwargs)
        user = order.user
        self.order = order
        self.to = []
        self.subject = "Ваш заказ на сайте %s успешно оформлен" % settings.SITE_DOMAIN
        client_info = OrderedDict()
        client_info['Email'] = user.email
        client_info['Телефон'] = user.profile.phone
        client_info['Выбранный магазин'] = order.takeout_point
        order_info = OrderedDict()
        order_info['Дата создания'] = timezone.localtime(order.created_at).strftime('%d.%m.%Y %H:%M')
        order_info['Комментарий к заказу'] = order.comment if len(order.comment) > 0 else 'Комментарий не задан'
        self.attach_alternative(
            render_to_string(
                'cart/order_manager_email.html',
                {
                    'order': order,
                    'payment_info': order.get_payment_type_display(),
                    'client_info': client_info,
                    'order_info': order_info,
                },
            ),
            'text/html',
        )


class OrderConfirmOnlinePaymentEmail(EmailMultiAlternatives):
    def __init__(self, order, *args, **kwargs):
        """

        """
        super().__init__(*args, **kwargs)
        user = order.user
        self.user = user
        self.order = order
        self.to = []
        self.subject = "Оплата прошла успешно"
        client_info = OrderedDict()
        client_info['Клиент'] = user.get_full_name
        client_info['Телефон'] = user.profile.phone
        client_info['Email'] = user.email
        client_info['Выбранный магазин'] = order.takeout_point
        order_info = OrderedDict()
        order_info['Дата создания'] = timezone.localtime(order.created_at).strftime('%d.%m.%Y %H:%M')
        order_info['Комментарий к заказу'] = order.comment if len(order.comment) > 0 else 'Комментарий не задан'
        self.attach_alternative(
            render_to_string(
                'cart/order_confirm_online_payment_email.html',
                {
                    'order': order,
                    'payment_info': order.get_payment_type_display(),
                    'client_info': client_info,
                    'order_info': order_info,
                },
            ),
            'text/html',
        )

class OrderConfirmOnlinePaymentClientEmail(EmailMultiAlternatives):
    def __init__(self, order, *args, **kwargs):
        """
        :param cart.models.Order order:
        """
        super().__init__(*args, **kwargs)
        user = order.user
        self.order = order
        self.to = [user.email]
        self.subject = "Ваш заказ на сайте %s успешно оплачен" % settings.SITE_DOMAIN
        client_info = OrderedDict()
        client_info['Email'] = user.email
        client_info['Телефон'] = user.profile.phone
        client_info['Выбранный магазин'] = order.takeout_point
        order_info = OrderedDict()
        order_info['Дата создания'] = timezone.localtime(order.created_at).strftime('%d.%m.%Y %H:%M')
        order_info['Комментарий к заказу'] = order.comment if len(order.comment) > 0 else 'Комментарий не задан'
        self.attach_alternative(
            render_to_string(
                'cart/client_confirmpayment_email.html',
                {
                    'order': order,
                    'payment_info': order.get_payment_type_display(),
                    'client_info': client_info,
                    'order_info': order_info,
                },
            ),
            'text/html',
        )
