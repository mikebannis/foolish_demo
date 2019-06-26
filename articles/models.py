from django.db import models
from django.template.defaultfilters import slugify as django_slugify
from django.http import Http404

import json
from datetime import datetime as dt

CONTENT = 'articles/data/content_api.json'
QUOTES = 'articles/data/quotes_api.json'

class Quote(models.Model):
    """ 
    Stock quote. This does not store all data from JSON.
    """
    company_name=models.CharField(max_length=100, null=True) 
    exchange=models.CharField(max_length=100, null=True) 
    symbol=models.CharField(max_length=100, null=True) 
    price=models.FloatField(null=True)
    change_amount=models.FloatField(null=True)
    percent_change=models.FloatField(null=True)
    # change_class is either 'positive' or 'negative'
    change_class=models.CharField(max_length=10, null=True)

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

            q, created = Quote.objects.get_or_create(company_name=company_name)
            q.exchange = new_q['Exchange']
            q.symbol = new_q['Symbol']
            q.price = new_q['CurrentPrice']['Amount']
            q.change_amount = new_q['Change']['Amount']

            percent_change = round(new_q['PercentChange']['Value']*100, 2)
            if percent_change >= 0:
                change_class = 'positive'
            else:
                change_class = 'negative'
            q.percent_change = percent_change
            q.change_class = change_class
            q.save()
            
            if created:
                new_count += 1
            else:
                exist_count +=1
        return companies, exist_count, new_count


class Tag(models.Model):
    """ 
    Article tags
    """
    slug=models.CharField(max_length=50)

    def __str__(self):
        return self.slug
    

class Article(models.Model):
    """ 
    Article model. This does not store all data from JSON.
    """
    article_slug=models.CharField(max_length=500, null=True) 
    body=models.TextField(null=True) 
    image_url=models.CharField(max_length=100, null=True) 
    headline=models.CharField(max_length=100, null=True) 
    author=models.CharField(max_length=100, null=True) 
    published_date=models.DateTimeField(null=True) 
    promo=models.CharField(max_length=100, null=True) 
    tags=models.ManyToManyField(Tag, related_name='articles')

    def __str__(self):
        return self.article_slug

    @staticmethod
    def slugify(headline):
        """ 
        Convert headline to url slug. Future versions should remove
        prepositions, articles, etc to shorten the url while maintaining
        readability.
        """
        return django_slugify(headline)
        
    @staticmethod
    def load_articles(articles_file=CONTENT): 
        """ 
        Create article entries in DB from JSON content file. Checks if article 
        already exists before creation. If it exists, update
        
        :param articles_file: path and filename of standard Fool JSON articles/content file
        :returns: art_slugs, exist_count, new_count
            art_slugs - list of article slugs in JSON
            exist_count - number articles in JSON already in DB
            new_count - number articles in JSON file not in DB
        """
        slugs = []
        exist_count = 0
        new_count = 0
        with open(CONTENT, 'rt') as f:
            new_articles = json.loads(f.readline())['results']  

        for new_article in new_articles:
            slug = Article.slugify(new_article['headline'])
            slugs.append(slug)

            art, created = Article.objects.get_or_create(article_slug=slug)

            # I have no idea what {%sfr%} is, but it's ugly and at the end of all 
            # articles. Remove it
            art.body = new_article['body'].split('{%sfr%}')[0]
            art.image_url = new_article['images'][0]['url']
            art.headline = new_article['headline']
            art.author = new_article['authors'][0]['byline']
            art.promo = new_article['promo']

            # Grab date before 'T': 2017-11-10T15:02:00Z
            date = dt.strptime(new_article['publish_at'].split('T')[0], '%Y-%m-%d')
            art.published_date=date
            art.save()

            tag_slugs = [tag['slug'] for tag in new_article['tags']] 
            art.tags.set([Tag.objects.get_or_create(slug=slug)[0] for slug in tag_slugs])
            art.save()
            
            if created:
                new_count += 1
            else:
                exist_count += 1
        return slugs, exist_count, new_count 

