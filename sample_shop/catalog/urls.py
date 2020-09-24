from django.urls import include, path
from .views import CatalogHomePageView, CategoryPageView

app_name = 'catalog'
urlpatterns = [
    path('', CatalogHomePageView.as_view(), name='index'),
    path('<str:slug>/', CategoryPageView.as_view(), name='category')
]
