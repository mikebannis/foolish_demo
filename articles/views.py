from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.template.defaultfilters import slugify

from .models import Articles

import json
import random
from datetime import datetime as dt

QUOTES = 'articles/data/quotes_api.json'
CONTENT = 'articles/data/content_api.json'

# -----------------------------------------------------
# ------------ Views ---------------------------------

def index(request):
    """ Index page for whole site """
    main_art_slug = 'is-goldman-sachs-stock-worth-a-look'
    main_art = Articles.objects.get(article_slug=main_art_slug)
    ra = RandArticle(main_art)
    context = {
        'main_art': main_art.prep_article(), 
        'left_art': ra.next().prep_article(),
        'mid_art': ra.next().prep_article(),
        'right_art': ra.next().prep_article(),
    }
    template = loader.get_template('index.html')
    return HttpResponse(template.render(context, request))

def article(request, art_slug=None):
    """ Render article body, comments, and stock quotes """
    ### TODO - check for None
    db_article = Articles.objects.get(article_slug=art_slug)
    art_json = db_article.get_json_data()
    #art = get_article(art_id)
    quotes = get_quotes()

    # Add additional info to quotes
    for q in quotes:
        q['MyChange'] = round(q['PercentChange']['Value']*100, 2)

        # Color coding for stock price change
        if q['MyChange'] >= 0:
            q['ChangeClass'] = 'positive'
        else:
            q['ChangeClass'] = 'negative'

    template = loader.get_template('articles/article.html')
    context = {'art_body': art_json['body'], 
               'quotes': quotes, 
               'db_article': db_article,
               #'art_stuff': prep_article(art_id),
    }
    return HttpResponse(template.render(context, request))

def load_articles(request):
    """ 
    Create article entries in DB from CONTENT file. Checks if article already exists
    before creation. If it exists, don't do anything
    """
    slugs = []
    count = 0
    new_articles = get_articles()
    for new_article in new_articles:
        slug = slugify(new_article['headline'])
        slugs.append(slug)
        try:
            _ = Articles.objects.get(article_slug=slug)
        except Articles.DoesNotExist:
            Articles.objects.create(article_slug=slug)
            count += 1
        
    return HttpResponse(f'<h1>Done! Created {count} new articles in the DB</h1> {slugs}')

# -----------------------------------------------------
# ------------ Helper functions -----------------------

class RandArticle(object):
    """ Used to select articles for index page. Prevents showing duplicate articles """
    def __init__(self, main_art):
        """ :param main_art: main article on homepage """
        print(list(Articles.objects.all()))
        self.arts = list(Articles.objects.all()).remove(main_art)
        # TODO: error handling below should be better
        #if self.num_art < 4:
        #    raise ValueError('There must be at least four articles for this to work')

    def next(self):
        """ Returns a random article, excluding those already used """
        art = random.choice(self.arts)
        self.arts.remove(art)
        return art
        #while True:
            #x = randint(0, self.num_art - 1)
            ##if x not in self.used_arts:
                #self.used_arts.append(x)
                #return x

#def prep_article(art_num):
#    """ Returns dict of article parts for article number art_num for site index page """
#    art = get_article(art_num)
#    # Grab date before 'T': 2017-11-10T15:02:00Z
#    date = dt.strptime(art['publish_at'].split('T')[0], '%Y-%m-%d')
#    date = date.strftime('%B %d, %Y')
#    x = {
#        'image': art['images'][0]['url'], 
#        'headline': art['headline'],
#        'author': art['authors'][0]['byline'],
#        'date': date,
#        'text': art['promo'],
#        'art_num': art_num,
#    }
#    return x

def get_articles():
    with open(CONTENT, 'rt') as f:
        content = json.loads(f.readline())
    return content['results']

def num_articles():
    """ Return number of articles in JSON file """
    articles = get_articles()
    return len(articles)
    
def get_article(num):
    """ Return article dict for article number 'num' (starts at 0) """
    articles = get_articles()
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
