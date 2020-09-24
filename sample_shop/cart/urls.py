from django.urls import include, path
from .views import CartView

app_name = 'cart'
urlpatterns = [
    path('', CartView.as_view(), name='index'),
]
