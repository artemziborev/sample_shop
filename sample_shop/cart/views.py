# Create your views here.
from django.urls import reverse
from django.views.generic.base import TemplateView
from django.utils.translation import gettext_lazy as _
from sample_shop.core.mixins import BreadcrumbsMixin


class CartView(TemplateView, BreadcrumbsMixin):
    template_name = 'cart/cart.html'

    def _get_breadcrumbs(self):
        return [{'name': _('Главная'), 'url': '/'}, {'name': _('Корзина'), 'url': reverse('cart:index')}]
