from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from django.template.defaultfilters import slugify

from .models import Article, Quote, Tag

import json
import random
from datetime import datetime as dt

# -----------------------------------------------------
# ------------ Views ---------------------------------

def index(request):
    """ 
    Index page for whole site. Shows a primary article and three secondary articles
    """
    # Grab first article with tag 10-promise
    tag = Tag.objects.get(slug='10-promise')
    main_art = tag.articles.all()[0]

    ra = RandArticle(main_art.article_slug)
    context = {
        'main_art': main_art, 
        'left_art': ra.next_article(),
        'mid_art': ra.next_article(),
        'right_art': ra.next_article(),
    }
    template = loader.get_template('index.html')
    return HttpResponse(template.render(context, request))

def article(request, art_slug=None):
    """ 
    Individual article page. Includes article body, comments, and stock quotes 
    """
    ### TODO - check for None, though I think that's not even possible
    article = get_object_or_404(Article, article_slug=art_slug)
    quotes = Quote.objects.all()

    template = loader.get_template('articles/article.html')
    context = { 'article': article,
                'quotes': quotes }
    return HttpResponse(template.render(context, request))

# -------------------------------------------------------------
# ------------ Utility and testing views -----------------------

def load_articles(request):
    """ 
    Create article entries in DB from CONTENT file. Checks if article already exists
    before creation. If it exists, update
    
    TODO:
    This is for testing purposes and clearly is not intended for use in production. 
    """
    slugs, exist_count, new_count = Article.load_articles()
    return HttpResponse(f'<h1>Done! Created {new_count} new articles in the DB</h1>' + \
                        f'<h2>Updated {exist_count} existing articles</h2>' + \
                        f'<h2>URL slugs found:</h2>{slugs}')

def load_quotes(request):
    """ 
    Create quotes entries in DB from QUOTES file. Checks if quote already exists
    before creation. If it exists, update
    
    TODO:
    This is for testing purposes and clearly is not intended for use in production. 
    """
    companies, exist_count, new_count = Quote.load_quotes()
    return HttpResponse(f'<h1>Done! Created {new_count} new quotes in the DB</h1>' + \
                        f'<h2>Updated {exist_count} existing quotes</h2>' + \
                        f'<h2>Quotes imported for the following companies:</h2>{companies}')

def slug_test(request):
    """ 
    Show all slugs for all articles. This was used as a QnD way of viewing all tags for 
    development purposes.
    """
    arts = Article.objects.all()
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
        self.arts = list(Article.objects.exclude(article_slug=main_art_slug))

    def next_article(self):
        """ Returns a random article, excluding those already used """
        try:
            art = random.choice(self.arts)
        except IndexError:
            raise ValueError('Requested random article but no articles remain')
        self.arts.remove(art)
        return art

