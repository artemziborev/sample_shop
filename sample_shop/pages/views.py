from crispy_forms.utils import render_crispy_form
from django.http import JsonResponse
from django.template.context_processors import csrf
from django.views.generic import CreateView
from django.views.generic import ListView
from django.views.generic.base import TemplateView

from sample_shop.catalog.models import Category
from sample_shop.products.models import Brand, BaseProduct
from .forms import CallBackRequestForm
from .models import BannersMain, MainNavItem, Certificate, TeamMember, FinishedWork, Manager, Advantage
from ..blog.models import Article


class IndexView(TemplateView):
    template_name = 'pages/home.html'

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['banners'] = BannersMain.objects.all()
    #     context['main_nav_items'] = MainNavItem.objects.all()
    #     context['brands'] = Brand.objects.all()
    #     context['categories'] = Category.objects.filter(parent=None)
    #     context['articles'] = Article.objects.filter(is_video_review=False).order_by('created')[:6]
    #     context['video_articles'] = Article.objects.filter(is_video_review=True).order_by('created')[:6]
    #     context['popular_products'] = BaseProduct.objects.filter(popularity__gte=3)
    #     return context


class AboutView(TemplateView):
    template_name = "pages/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['advantages'] = Advantage.objects.all()
        context['certificates'] = Certificate.objects.all()
        context['finished_works'] = FinishedWork.objects.all()
        context['team_members'] = TeamMember.objects.all()
        return context


class ContactsView(TemplateView):
    template_name = "pages/contacts.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['managers'] = Manager.objects.all()
        return context


class NewsView(TemplateView):
    template_name = "blog/news.html"


class NewsPageView(TemplateView):
    template_name = 'blog/news-page.html'


class BrandsListView(ListView):
    model = Brand
    template_name = 'pages/brands_list.html'


class CallbackView(CreateView):
    def _get_message(self):
        return 'Сообщение отправлено'

    def _get_valid_initial(self, valid):
        return {}

    def form_valid(self, form):
        self.object = form.save()
        if hasattr(self.object, 'send_email'):
            self.object.send_email()
        context = {}
        context.update(csrf(self.request))
        return JsonResponse({
            'message': self._get_message(),
            'html': render_crispy_form(self.form_class(
                # Тут мы передаём значение поля form_type для корректного отображения после отправки формы в конструктор,
                # чтобы после отправки она не переключалась на стандартную
                form.fields['form_type'].initial,
                initial=self._get_valid_initial(form)),
                context=context
            )
        })

    def form_invalid(self, form):
        context = {}
        context.update(csrf(self.request))
        return JsonResponse({
            'html': render_crispy_form(form, context=context)
        }, status=400)


class CallbackCreateView(CallbackView):
    form_class = CallBackRequestForm
