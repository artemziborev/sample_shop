from django.urls import path

from . import views

app_name = 'blog'
urlpatterns = [
    path('', views.ArticleListView.as_view(), name='index'),
    path('<str:slug>/', views.ArticleDetailView.as_view(), name='article'),
]
