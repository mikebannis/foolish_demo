from django.db import models

# Article model for linking comments. Article info is kept in JSON file
class Articles(models.Model):
     article_slug=models.CharField(max_length=500, null=True) 
