"""
Tests for the articles app. Tests are setup to use backup data in case quotes and content
JSON files are changed. 
""" 
from django.test import TestCase, Client

from . import models
from . import views

TEST_QUOTES = 'articles/test_data/quotes_api.json'
TEST_CONTENT = 'articles/test_data/content_api.json'

class ViewsTestCase(TestCase):
    def setUp(self):
        models.Article.load_articles(articles_file=TEST_CONTENT)
        models.Quote.load_quotes(quotes_file=TEST_QUOTES)
        self.client = Client()

    def test_articles(self):
        response = self.client.get('/articles/51job-accelerates-to-get-the-job-done')
        self.assertEqual(response.status_code, 301)
        response = self.client.get('/articles/51job-accelerates-to-get-the-job-done/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['quotes']), 24)

    def test_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['main_art'].article_slug, 'heres-why-barrrick-gold-plunged-10-in-october')

class QuotesTestCase(TestCase):
    def setUp(self):
        models.Quote.load_quotes(quotes_file=TEST_QUOTES)

    def test_get_quotes(self):
        x = list(models.Quote.objects.all())
        self.assertEqual(len(x), 24)
        self.assertEqual(x[0].company_name, 'Goldman Sachs')

class ArticleTestCase(TestCase):
    def setUp(self):
        models.Article.load_articles(articles_file=TEST_CONTENT)
        models.Quote.load_quotes(quotes_file=TEST_QUOTES)
    
    def test_attributes(self):
        x = models.Article.objects.get(article_slug='is-goldman-sachs-stock-worth-a-look')
        self.assertEqual(x.headline, 'Is Goldman Sachs\' Stock Worth a Look?')
        self.assertEqual(x.promo, 'Three reasons to think that Goldman Sachs’ stock is reasonably priced.')
        self.assertEqual(x.image_url, 'https://g.foolcdn.com/editorial/images/463175/goldman-sachs-tower.jpg')

    def test_tags(self):
        x = models.Article.objects.get(article_slug='51job-accelerates-to-get-the-job-done')

        real_tags = ['msn', 'yahoo-news', 'default-partners']
        for tag in real_tags:
            test_tag = models.Tag.objects.get(slug=tag)
            self.assertEqual(test_tag, x.tags.get(slug=tag))

        with self.assertRaises(models.Tag.DoesNotExist):
            x.tags.get(slug='10-promise')

        false_tags = ['20-promise', 'yahoo-monEy', 'go0ogle']
        for tag in false_tags:
            with self.assertRaises(models.Tag.DoesNotExist):
                test_tag = models.Tag.objects.get(slug=tag)

    def test_get_last_10_promise(self):
        tag = models.Tag.objects.get(slug='10-promise')
        main_art = tag.articles.first()
        #print('main_art:', main_art)
        self.assertEqual(main_art.article_slug, 'heres-why-barrrick-gold-plunged-10-in-october')
