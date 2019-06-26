from django.contrib import admin

from .models import Article, Quote, Tag

# Register your models here.
admin.site.register(Article)
admin.site.register(Quote)
admin.site.register(Tag)

