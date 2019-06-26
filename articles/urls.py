from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),

    # load_articles and slug_test are for testing only
    path('load_articles/', views.load_articles, name='load_articles'),
    path('load_quotes/', views.load_quotes, name='load_quotes'),
    path('slug_test/', views.slug_test),

    # The below line will catch almost anything in addition to article headline
    # slugs and should be the last line in urlpatterns
    path('<str:art_slug>/', views.article, name='article'),
]
