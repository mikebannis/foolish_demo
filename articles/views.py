from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.template.defaultfilters import slugify

from .models import Articles

import json
import random
from datetime import datetime as dt

QUOTES = 'articles/data/quotes_api.json'

# -----------------------------------------------------
# ------------ Views ---------------------------------

def index(request):
    """ 
    Index page for whole site. Shows a primary article and three secondary articles
    """
    main_art = Articles.get_first_with_tag('10-promise')
    #main_art = Articles.get_first_with_tag('test tag slug')
    ra = RandArticle(main_art.article_slug)
    context = {
        'main_art': main_art.prep_article(), 
        'left_art': ra.next().prep_article(),
        'mid_art': ra.next().prep_article(),
        'right_art': ra.next().prep_article(),
    }
    template = loader.get_template('index.html')
    return HttpResponse(template.render(context, request))

def article(request, art_slug=None):
    """ 
    Individual article page. Includes article body, comments, and stock quotes 
    """
    ### TODO - check for None, though I think that's not even possible
    db_article = Articles.objects.get(article_slug=art_slug)
    quotes = get_quotes()

    # Add additional info to quotes for presentation
    for q in quotes:
        q['MyChange'] = round(q['PercentChange']['Value']*100, 2)

        # Color coding for stock price change
        if q['MyChange'] >= 0:
            q['ChangeClass'] = 'positive'
        else:
            q['ChangeClass'] = 'negative'

    template = loader.get_template('articles/article.html')
    context = { 'quotes': quotes, 
               'db_article': db_article,
               'art_data': db_article.prep_article(),
    }
    return HttpResponse(template.render(context, request))

# -------------------------------------------------------------
# ------------ Utility and testing views -----------------------

def load_articles(request):
    """ 
    Create article entries in DB from CONTENT file. Checks if article already exists
    before creation. If it exists, don't do anything
    
    TODO:
    This is for testing purposes and clearly is not intended for use in production. 
    """
    slugs = []
    count = 0
    # I shouldn't be calling a hidden method directly, but it's only for testing
    new_articles = Articles._get_articles_json()
    for new_article in new_articles:
        slug = slugify(new_article['headline'])
        slugs.append(slug)
        try:
            _ = Articles.objects.get(article_slug=slug)
        except Articles.DoesNotExist:
            Articles.objects.create(article_slug=slug)
            count += 1
        
    return HttpResponse(f'<h1>Done! Created {count} new articles in the DB</h1>' + \
                        f'<h2>URL slugs found:</h2>{slugs}')

def slug_test(request):
    """ 
    Show all slugs for all articles. This was used as a QnD way of viewing all tags.
    """
    arts = [x.get_json_data() for x in Articles.objects.all()]
    context = {'articles': arts}
    template = loader.get_template('articles/slug_test.html')
    return HttpResponse(template.render(context, request))

# -----------------------------------------------------------
# ------------ Helper classes/functions -----------------------

class RandArticle(object):
    """ 
    Return random articles. Used to select articles for index page. 
    Prevents showing duplicate articles.
    """
    def __init__(self, main_art_slug):
        """ :param main_art_slug: slug for main article on homepage """
        self.arts = list(Articles.objects.exclude(article_slug=main_art_slug))

    def next(self):
        """ Returns a random article, excluding those already used """
        try:
            art = random.choice(self.arts)
        except IndexError:
            raise ValueError('Requested random article but no articles remain')
        self.arts.remove(art)
        return art

def get_quotes():
    """ Return quotes list as list of dicts"""
    with open(QUOTES, 'rt') as f:
        quotes = json.loads(f.readline())
    return quotes

