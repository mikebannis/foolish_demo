from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<str:art_slug>/', views.article, name='article'),
    path('load_articles/', views.load_articles, name='load_articles')
]
