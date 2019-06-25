"""
Tests for the articles app. Tests are setup to use backup data in case quotes and content
JSON files are changed. 
""" 
from django.test import TestCase, Client

from . import models
from . import views

class ViewsTestCase(TestCase):
    def setUp(self):
        views.QUOTES = 'articles/test_data/quotes_api.json'
        models.CONTENT = 'articles/test_data/content_api.json'
        models.Article.objects.create(article_slug='why-atlassian-corporation-plc-stock-gained-376-in-october')
        models.Article.objects.create(article_slug='why-ncr-corporation-stock-lost-145-in-october')
        models.Article.objects.create(article_slug='51job-accelerates-to-get-the-job-done')
        models.Article.objects.create(article_slug='3-takeaways-from-intel-corps-10-q-filing')
        self.client = Client()

    def test_articles(self):
        response = self.client.get('/articles/51job-accelerates-to-get-the-job-done')
        self.assertEqual(response.status_code, 301)
        response = self.client.get('/articles/51job-accelerates-to-get-the-job-done/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['quotes']), 25)

    def test_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['main_art']['art_slug'], 'why-atlassian-corporation-plc-stock-gained-376-in-october')

class QuotesTestCase(TestCase):
    def setUp(self):
        views.QUOTES = 'articles/test_data/quotes_api.json'

    def test_get_quotes(self):
        x = views.get_quotes()
        self.assertEqual(len(x), 25)
        self.assertEqual(x[0]['CompanyName'], 'Goldman Sachs')

class ArticleTestCase(TestCase):
    def setUp(self):
        models.CONTENT = 'articles/test_data/content_api.json'
        models.Article.objects.create(article_slug='is-goldman-sachs-stock-worth-a-look')
        models.Article.objects.create(article_slug='why-ncr-corporation-stock-lost-145-in-october')
    
    def test_json(self):
        x = models.Article.objects.get(article_slug='is-goldman-sachs-stock-worth-a-look')
        data = x.get_json_data()
        self.assertEqual(data['headline'], "Is Goldman Sachs' Stock Worth a Look?")
        self.assertEqual(data['promo'], 'Three reasons to think that Goldman Sachs’ stock is reasonably priced.')

    def test_prep(self):
        x = models.Article.objects.get(article_slug='is-goldman-sachs-stock-worth-a-look')
        d = x.prep_article()
        self.assertEqual(d['headline'], "Is Goldman Sachs' Stock Worth a Look?")
        self.assertEqual(d['text'], 'Three reasons to think that Goldman Sachs’ stock is reasonably priced.')
        self.assertEqual(d['image'],'https://g.foolcdn.com/editorial/images/463175/goldman-sachs-tower.jpg')
    
    def test_tags(self):
        x = models.Article.objects.get(article_slug='is-goldman-sachs-stock-worth-a-look')
        self.assertTrue(x.tag_exists('msn'))
        self.assertFalse(x.tag_exists('10-promise'))
        x = models.Article.objects.get(article_slug='why-ncr-corporation-stock-lost-145-in-october')
        self.assertFalse(x.tag_exists('google'))
        self.assertTrue(x.tag_exists('10-promise'))

    def test_get_first(self):
        x = models.Article.get_first_with_tag('10-promise')
        # Note this is not the first article with '10-promise' on the site, as we're
        # using a test DB
        self.assertEqual(x.article_slug, 'why-ncr-corporation-stock-lost-145-in-october')
        with self.assertRaises(ValueError):
            models.Article.get_first_with_tag('not-a-real-tag') 
