from django.shortcuts import render
from django.urls import reverse
from django.views.generic import DetailView

from .models import SubProduct, BaseProduct

from sample_shop.core.mixins import BreadcrumbsMixin

class ProductDetailView(DetailView):
    model = SubProduct
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['breadcrumbs'] = [{'name': 'Главная', 'url': '/'}, {'name': 'Каталог', 'url': reverse('catalog:index')}]
        context['breadcrumbs'] += [{'name': self.object.name, 'url': '#'}]
        if 'last_viewed' not in self.request.session:
            self.request.session['last_viewed'] = []
        last_viewed = list(self.request.session['last_viewed'])
        if self.object.base_product.id in last_viewed:
            last_viewed.remove(self.object.base_product.id)
        context['last_viewed_product_list'] = BaseProduct.objects.filter(id__in=last_viewed)
        last_viewed.append(self.object.base_product.id)
        self.request.session['last_viewed'] = last_viewed
        return context


product_detail_view = ProductDetailView.as_view()
