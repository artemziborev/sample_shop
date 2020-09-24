from django.urls import reverse
from django.views.generic import ListView, DetailView
from django.utils.translation import gettext_lazy as _
from sample_shop.blog.models import Article
from sample_shop.core.mixins import BreadcrumbsMixin


class ArticleListView(ListView, BreadcrumbsMixin):
    paginate_by = 1
    model = Article

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def _get_breadcrumbs(self):
        return [{'name': _('Главная'), 'url': '/'}, {'name': _('Статьи'), 'url': reverse('blog:index')}]


class ArticleDetailView(DetailView, BreadcrumbsMixin):
    model = Article

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['breadcrumbs'] = [
            {'name': _('Главная'), 'url': '/'},
            {'name': _('Статьи'), 'url': reverse('blog:index')},
            {'name': context['object'], 'url': reverse('blog:article', args=[context['object'].slug])},
        ]
        return context
