from django.views.generic.base import ContextMixin


class BreadcrumbsMixin(ContextMixin):
    def _get_breadcrumbs(self):
        return []

    def get_breadcrumbs(self):
        return self._get_breadcrumbs()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = self.get_breadcrumbs()
        return context
