from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from django.template.defaultfilters import slugify

from .models import Articles, Quotes

import json
import random
from datetime import datetime as dt

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
    article = get_object_or_404(Articles, article_slug=art_slug)
    quotes = Quotes.objects.all()

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
    slugs = []
    exist_count = 0
    new_count = 0
    # I shouldn't be calling a hidden method directly, but it's only for testing
    new_articles = Articles._get_articles_json()
    for new_article in new_articles:
        slug = slugify(new_article['headline'])
        slugs.append(slug)

        # Grab date before 'T': 2017-11-10T15:02:00Z
        date = dt.strptime(new_article['publish_at'].split('T')[0], '%Y-%m-%d')
        try:
            art = Articles.objects.get(article_slug=slug)
            art.body=new_article['body']
            art.image_url=new_article['images'][0]['url']
            art.headline=new_article['headline']
            art.author=new_article['authors'][0]['byline']
            art.published_date=date
            art.promo=new_article['promo']
            art.save()
            #art.other_data=new_article)
            exist_count +=1
        except Articles.DoesNotExist:
            Articles.objects.create(article_slug=slug,
                                    body=new_article['body'],
                                    image_url=new_article['images'][0]['url'],
                                    headline=new_article['headline'],
                                    author=new_article['authors'][0]['byline'],
                                    published_date=date,
                                    promo=new_article['promo'])
                                    #other_data=new_article)
            new_count += 1
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
    companies, exist_count, new_count = Quotes.load_quotes()

    return HttpResponse(f'<h1>Done! Created {new_count} new quotes in the DB</h1>' + \
                        f'<h2>Updated {exist_count} existing quotes</h2>' + \
                        f'<h2>Quotes imported for the following companies:</h2>{companies}')
def slug_test(request):
    """ 
    Show all slugs for all articles. This was used as a QnD way of viewing all tags for 
    development purposes.
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

    def next_article(self):
        """ Returns a random article, excluding those already used """
        try:
            art = random.choice(self.arts)
        except IndexError:
            raise ValueError('Requested random article but no articles remain')
        self.arts.remove(art)
        return art

