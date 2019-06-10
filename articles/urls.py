from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:art_id>/', views.article, name='article'),
    path('load_articles/', views.load_articles, name='load_articles')
]
