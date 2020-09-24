from django.urls import path, include
from .views import AboutView, ContactsView, IndexView, BrandsListView, CallbackCreateView

app_name = 'pages'
urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('about/', AboutView.as_view(), name='about'),
    path('contacts/', ContactsView.as_view(), name='contacts'),
    path('pages/', include('django.contrib.flatpages.urls')),
    path('brands/', BrandsListView.as_view(), name='brands'),
    path('callbackform/', CallbackCreateView.as_view(), name='callback_form')
]
