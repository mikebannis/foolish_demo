from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

import json

DEBUG = False  # for running this file directly for testing

if not DEBUG:
    CONTENT = 'articles/data/content_api.json'
    QUOTES = 'articles/data/quotes_api.json'
else:
    CONTENT = 'data/content_api.json'
    QUOTES = 'data/quotes_api.json'

# Create your views here.

def index(request):
    """ Index page for whole site """
    return HttpResponse('heres the site index page!!!')

def article(request, art_id=None):
    """ Render article body """
    ### TODO - check for None
    art = get_article(art_id)
    quotes = get_quotes()
    template = loader.get_template('articles/article.html')

    # Add additional info to quotes
    for i, q in enumerate(quotes):
        q['MyChange'] = round(q['PercentChange']['Value']*100, 2)
        if q['MyChange'] >= 0:
            q['ChangeClass'] = 'positive'
        else:
            q['ChangeClass'] = 'negative'
        q['QuoteNum'] = 'Quote_' + str(i)
        
    context = {'art_body': art['body'], 'quotes': quotes}
    return HttpResponse(template.render(context, request))

def OLD_article(request, art_id=None):
    """ Render article body """
    ### TODO - check for None
    art = get_article(art_id)
    return HttpResponse(art['body'])

# ------------ Helper functions -----------------------
def get_article(num):
    """ Return article dict for article number 'num' (starts at 0) """
    with open(CONTENT, 'rt') as f:
        content = json.loads(f.readline())
    articles = content['results']
    len_art = len(articles)
    if num >= len_art:
        raise AttributeError(f'Requested article {num}. Maximum article' + \
                              f' number is {len_art}')
    return articles[num]

def get_quotes():
    """ Return quotes list """
    with open(QUOTES, 'rt') as f:
        quotes = json.loads(f.readline())
    return quotes

def main():
    qs = get_quotes()
    for q in qs:
        print (q)

if __name__ == '__main__':
    main()
