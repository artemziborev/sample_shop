import re

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

User = get_user_model()

class CartAssemblyRequestEMail(EmailMessage):
    def __init__(self, assembly, *args, **kwargs):
        """
        :param cart.models.CartAssemblyRequest assembly:
        :param args:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)
        self.user = assembly.user
        self.assembly = assembly
        self.to = [self.user.email]
        self.subject = _('Ваша заявка на сайте успешно отправлена')
        self.content_subtype = 'html'
        self.body = render_to_string(
            'cart/cart_assembly_request_email.html',
            {
                'phone': self.assembly.takeout_point.phone,
                'phone_filtered': re.sub(r"[\s\-()]", "", self.assembly.takeout_point.phone),
                'site_link': "https://%s" % settings.SITE_DOMAIN,
                'site_name': settings.SITE_DOMAIN,
                'client_info': {_('Клиент'): self.user.get_full_name},
                'assembly_info': {
                    _("Комментарий к заказу"): assembly.comment if len(assembly.comment) > 0 else _("Комментарий не задан")
                },
                'assembly': self.assembly,
            },
        )


class CartAssemblyRequestAcceptedEmail(EmailMessage):
    def __init__(self, assembly, *args, **kwargs):
        """
        :param cart.models.CartAssemblyRequest assembly:
        :param args:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)
        self.subject = _('Заявка на сбор была утверждена')
        self.body = assembly.accepted_message
        self.to = [assembly.user.email]
        self.attach_file(assembly.file.path)
        for file in assembly.files.all():
            self.attach_file(file.file.path)


class CartAssemblyRequestRejectedEmail(EmailMessage):
    def __init__(self, assembly, *args, **kwargs):
        """
        :param cart.models.CartAssemblyRequest assembly:
        :param args:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)
        self.subject = _('Ваша заявка на сбор было отклонена')
        self.body = assembly.rejected_message
        self.to = [assembly.user.email]


class CartAssemblyRequestManagerEmail(EmailMessage):
    def __init__(self, assembly, *args, **kwargs):
        """
        :param cart.models.CartAssemblyRequest assembly:
        :param args:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)
        self.content_subtype = 'html'
        self.subject = _('Получена новая заявка с сайта')
        manager_email_list = assembly.user.profile.get_manager_emails()
        shop_email_list = assembly.user.profile.get_shop_email_list()
        self.to = []
        if len(manager_email_list) > 0:
            self.to += manager_email_list
        elif len(shop_email_list):
            self.to += shop_email_list
        elif assembly.takeout_point.email:
            self.to += [assembly.takeout_point.email]
        profile = assembly.user.profile
        pattern = re.compile('<(?P<email>.*)>')
        try:
            if len(manager_email_list) > 0:
                email = pattern.search(manager_email_list[0]).group('email')
            elif len(shop_email_list):
                email = pattern.search(shop_email_list[0]).group('email')
            elif assembly.takeout_point.email:
                email = assembly.takeout_point.email
            else:
                email = 'manager@manager.ru'
            user = get_user_model().objects.get(email=email)
        except get_user_model().DoesNotExist:
            user = get_user_model().objects.get(email='manager@manager.ru')
        self.body = render_to_string(
            'cart/cart_assembly_request_manager_email.html',
            {
                'site_link': 'https://{}'.format(settings.SITE_DOMAIN),
                'assembly': assembly,
                'assembly_info': {
                    _('Комментарий к заказу'): assembly.comment if len(assembly.comment) > 0 else
                    _('Комментарий не задан')
                },
            },
        )
