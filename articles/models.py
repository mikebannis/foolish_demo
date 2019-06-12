from django.db import models
from django.template.defaultfilters import slugify as django_slugify
from django.http import Http404

import json
from datetime import datetime as dt

CONTENT = 'articles/data/content_api.json'

class Articles(models.Model):
    """ 
    Article model for linking comments. Article info is kept in JSON file and 
    should be obtained using get_json_data() or prep_article()
    """
    article_slug=models.CharField(max_length=500, null=True) 

    def get_json_data(self):
        """ Return dict of article info represented by self from JSON file """
        arts = self._get_articles_json()
        for art in arts:
            if self.slugify(art['headline']) == self.article_slug:
                return art
        # TODO: http404 is wrong, if we get here something is wrong in the DB 
        # (or this code), notify admin
        raise Http404

    def prep_article(self):
        """ Returns dict of article parts to be used as context for rendering """
        json_data = self.get_json_data()

        # Grab date before 'T': 2017-11-10T15:02:00Z
        date = dt.strptime(json_data['publish_at'].split('T')[0], '%Y-%m-%d')
        date = date.strftime('%B %d, %Y')
        return {
            # I'm not sure what {%sfr%} is, but it's at the end of all the articles
            # and ugly so let's get rid of it
            'body': json_data['body'].split('{%sfr%}')[0],
            'image': json_data['images'][0]['url'],
            'headline': json_data['headline'],
            'author': json_data['authors'][0]['byline'],
            'date': date,
            'text': json_data['promo'],
            'art_slug': self.article_slug,
        }
    
    def tag_exists(self, tag_slug):
        """ 
        Returns True if one of the tag slugs is 'tag_slug'. Otherwise, return 
        False 
        """
        json_data = self.get_json_data()
        for tag in json_data['tags']:  
            if tag['slug'] == tag_slug:
                return True
        return False

    @staticmethod
    def get_first_with_tag(tag):
        """ Return first article object in DB with tag slug 'tag' """
        arts = Articles.objects.all()
        for art in arts:
            if art.tag_exists(tag):
                return art
        raise ValueError(f'No article with tag {tag} found!')
        
    @staticmethod    
    def _get_articles_json():
        """ Return all articles as list of dicts from CONTENT JSON file """
        with open(CONTENT, 'rt') as f:
            content = json.loads(f.readline())
        return content['results']

    @staticmethod
    def slugify(headline):
        """ 
        Convert headline to url slug. Future versions should remove
        prepositions, articles, etc to shorten the url while maintaining
        readability.
        """
        return django_slugify(headline)

    def __str__(self):
        return self.article_slug

