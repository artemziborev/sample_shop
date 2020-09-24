from django.urls import reverse
from django.views.generic import ListView

from sample_shop.core.mixins import BreadcrumbsMixin
from sample_shop.products import models as product_models
from sample_shop.products import forms as product_forms
from . import models


class CatalogHomePageView(ListView, BreadcrumbsMixin):
    template_name = 'catalog/prods.html'
    model = models.Category
    context_object_name = 'categories'

    def _get_breadcrumbs(self):
        return [{'name': 'Главная', 'url': '/'}, {'name': 'Каталог продукции', 'url': reverse('catalog:index')}]


class CategoryPageView(ListView):
    template_name = 'catalog/category.html'
    model = product_models.BaseProduct
    context_object_name = 'products'

    def get_queryset(self, **kwargs):
        category = models.Category.objects.get(slug=self.kwargs.get('slug'))
        return product_models.BaseProduct.objects.filter(categories__in=category.get_descendants(include_self=True))

    def get_context_data(self, **kwargs):
        objects = self.get_queryset()
        context = super().get_context_data()
        context['filter_form'] = product_forms.FilterForm()
        context['categories'] = models.Category.objects.all()
        context['colors'] = product_models.Color.objects.filter(products_list__in=objects)
        context['materials'] = product_models.Material.objects.filter(product_list__in=objects)
        context['brands'] = product_models.Brand.objects.filter(products_list__in=objects)
        return context
