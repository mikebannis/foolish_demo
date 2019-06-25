from django.db import models
from django.template.defaultfilters import slugify as django_slugify
from django.http import Http404

import json
from datetime import datetime as dt

CONTENT = 'articles/data/content_api.json'
QUOTES = 'articles/data/quotes_api.json'

class Quotes(models.Model):
    """ 
    Stock quote. 
    """
    company_name=models.CharField(max_length=100, null=True) 
    exchange=models.CharField(max_length=100, null=True) 
    symbol=models.CharField(max_length=100, null=True) 
    price=models.FloatField(null=True)
    change_amount=models.FloatField(null=True)
    percent_change=models.FloatField(null=True)
    # change_class is either 'positive' or 'negative'
    change_class=models.CharField(max_length=10, null=True)
    #other_data= # json dict

    def __str__(self):
        return self.company_name

    @staticmethod
    def load_quotes(quotes_file=QUOTES):
        """
        Create quotes entries in DB from JSON quotes file. Checks if quote 
        already exists before creation. If it exists, update
        
        :param quotes_file: path and filename of standard Fool JSON stock quotes
        :returns: companies, exist_count, new_count
            companies - list of names of companies w/ quotes in JSON
            exist_count - number of companies in JSON already in DB
            new_count - number of companies in JSON file not in DB
        """
        companies = []
        exist_count = 0
        new_count = 0

        with open(quotes_file, 'rt') as f:
            quotes = json.loads(f.readline())

        for new_q in quotes:
            company_name = new_q['CompanyName']
            companies.append(company_name)
            percent_change = round(new_q['PercentChange']['Value']*100, 2)
            if percent_change >= 0:
                change_class = 'positive'
            else:
                change_class = 'negative'

            try:
                q=Quotes.objects.get(company_name=company_name)
                q.exchange=new_q['Exchange']
                q.symbol=new_q['Symbol']
                q.price=new_q['CurrentPrice']['Amount']
                q.change_amount=new_q['Change']['Amount']
                q.percent_change=percent_change
                q.change_class=change_class
                q.save()
                #art.other_data=new_article)
                exist_count +=1
            except Quotes.DoesNotExist:
                Quotes.objects.create(company_name=company_name,
                                        exchange=new_q['Exchange'],
                                        symbol=new_q['Symbol'],
                                        price=new_q['CurrentPrice']['Amount'],
                                        change_amount=new_q['Change']['Amount'],
                                        percent_change=percent_change,
                                        change_class=change_class,)
                new_count += 1
        return companies, exist_count, new_count


class Articles(models.Model):
    """ 
    Article model. 
    """
    article_slug=models.CharField(max_length=500, null=True) 
    body=models.TextField(null=True) 
    image_url=models.CharField(max_length=100, null=True) 
    headline=models.CharField(max_length=100, null=True) 
    author=models.CharField(max_length=100, null=True) 
    published_date=models.DateTimeField(null=True) 
    promo=models.CharField(max_length=100, null=True) 
    #other_data= # json dict

    def get_json_data(self):
        """ Return dict of article info represented by self from JSON file """
        ##########################
        # TODO: still used by tag_exists() - get rid of this!!!!
        ##########################
        arts = self._get_articles_json()
        for art in arts:
            if self.slugify(art['headline']) == self.article_slug:
                return art
        # TODO: http404 is wrong, if we get here something is wrong in the DB 
        # (or this code), notify admin
        raise Http404
    
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
    def slugify(headline):
        """ 
        Convert headline to url slug. Future versions should remove
        prepositions, articles, etc to shorten the url while maintaining
        readability.
        """
        return django_slugify(headline)
        
    @staticmethod    
    def _get_articles_json():
        """ Return all articles as list of dicts from CONTENT JSON file """
        with open(CONTENT, 'rt') as f:
            content = json.loads(f.readline())
        return content['results']

    def __str__(self):
        return self.article_slug

