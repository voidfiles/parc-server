from datetime import datetime, timedelta

from django.test import TestCase
import json
import os
import responses

from catalog.models import Article, ARTICLE_STATUS
from catalog.schemas.base import PARC_ISO_STRF_FORMAT

DEFAULT_ARTICLE_URL = 'http://recode.net/2014/12/04/amazon-unveils-its-own-line-of-diapers-confirming-partners-biggest-fears/'

BASE_DIR = os.path.dirname(__file__) + '/data/'

DEFAULT_ARTICLE_CONTENT = ''
with open(BASE_DIR + 'article.html') as fd:
    DEFAULT_ARTICLE_CONTENT = fd.read()

BASE_DIR = os.path.dirname(__file__) + '/data/'
CASSETTE_DIR = BASE_DIR + '/cassettes/'


class MockModel(object):
    DEFAULT_ARTICLE_CONTENT = DEFAULT_ARTICLE_CONTENT
    CASSETTE_DIR = CASSETTE_DIR
    DEFAULT_ARTICLE_URL = DEFAULT_ARTICLE_URL

    def add_article_content_to_responses(self, url=DEFAULT_ARTICLE_URL, body=DEFAULT_ARTICLE_CONTENT):
        responses.add(responses.GET, url,
                      body=body, status=200,
                      content_type='text/html')

    def create_article(self, extra_data=None):
        article = {
            'url': self.DEFAULT_ARTICLE_URL,
            'tags': [{'name': 'diaper'}, {'name': 'DIAPER'}]
        }

        if extra_data:
            article.update(extra_data)

        with responses.mock:
            self.add_article_content_to_responses()

            response = self.client.post('/api/v1/articles', json.dumps(article), content_type='application/json')

        return response

    def json_resp(self, url, data=None, method=None, assert_status_code=None,  *args, **kwargs):
        kwargs.setdefault('content_type', 'application/json')

        if data and method in ('post', 'put'):
            data = json.dumps(data)

        resp = getattr(self.client, method)(url, data, *args, **kwargs)
        if assert_status_code:
            self.assertEqual(assert_status_code, resp.status_code)

        parsed_resp = json.loads(resp.content)

        return parsed_resp.get('data', {}), parsed_resp['meta']

    def api_get(self, *args, **kwargs):
        return self.json_resp(method='get', *args, **kwargs)

    def api_post(self, *args, **kwargs):
        return self.json_resp(method='post', *args, **kwargs)

    def api_put(self, *args, **kwargs):
        return self.json_resp(method='put', *args, **kwargs)

    def api_delete(self, *args, **kwargs):
        return self.json_resp(method='delete', *args, **kwargs)


class TestArticles(MockModel, TestCase):

    def test_add_article(self):
        response = self.create_article()

        self.assertEqual(response.status_code, 200)
        resp = json.loads(response.content)

        self.assertEquals(resp['data']['title'], "Amazon Unveils Its Own Diapers and Baby Wipes Called Amazon Elements | Re/code")

    def test_add_article_failure(self):

        response = self.client.post('/api/v1/articles', json.dumps({
            'url': 'awesome'
        }), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        resp = json.loads(response.content)

        self.assertEquals(resp['meta']['error_info']['url'][0], "Not a well formed URL.")

    def test_article_pagination(self):
        base_url = 'http://example.com/article/%s'
        with responses.mock:
            for i in range(0, 20):
                url = base_url % i
                self.add_article_content_to_responses(url=url)

                response = self.client.post('/api/v1/articles', json.dumps({
                    'url': url,
                }), content_type='application/json')
                resp = json.loads(response.content)
                self.assertEqual(response.status_code, 200)

            response = self.client.get('/api/v1/articles?count=10')
        self.assertEqual(response.status_code, 200)
        resp = json.loads(response.content)
        assert len(resp['data']) == 10
        assert resp['meta']['min_id'] > 1

    def test_article_delete(self):
        response = self.create_article()
        resp = json.loads(response.content)
        response = self.client.delete('/api/v1/articles/%s' % (resp['data']['id']))
        self.assertEqual(response.status_code, 200)

        article = Article.objects.get(id=resp['data']['id'])
        self.assertEqual(article.status, ARTICLE_STATUS.DELETED)

    def test_article_archive(self):
        response = self.create_article()
        resp = json.loads(response.content)
        response = self.client.post('/api/v1/articles/%s/archive' % (resp['data']['id']))
        self.assertEqual(response.status_code, 200)

        article = Article.objects.get(id=resp['data']['id'])
        self.assertEqual(article.status, ARTICLE_STATUS.ARCHIVED)

    def test_article_unarchive(self):
        response = self.create_article()
        resp = json.loads(response.content)
        response = self.client.delete('/api/v1/articles/%s/archive' % (resp['data']['id']))
        self.assertEqual(response.status_code, 200)

        article = Article.objects.get(id=resp['data']['id'])
        self.assertEqual(article.status, ARTICLE_STATUS.UNREAD)

    def test_alter_article(self):
        response = self.create_article()
        resp = json.loads(response.content)

        model = resp['data']
        model['deleted'] = True
        del model['html']
        del model['title']
        model['date_updated'] = (datetime.utcnow() + timedelta(hours=2)).strftime(PARC_ISO_STRF_FORMAT)
        response = self.client.post('/api/v1/articles/%s' % (resp['data']['id']), content_type='application/json', data=json.dumps(model))
        self.assertEqual(response.status_code, 200)

        article = Article.objects.get(id=resp['data']['id'])
        self.assertEqual(article.status, ARTICLE_STATUS.DELETED)

    def test_last_write_win(self):
        response = self.create_article()
        resp = json.loads(response.content)

        article = Article.objects.get(id=int(resp['data']['id']))

        article.updated = datetime.utcnow() - timedelta(hours=1)
        article.save()
        model_data = resp['data']
        model_data['date_updated'] = (datetime.utcnow() + timedelta(hours=2)).strftime(PARC_ISO_STRF_FORMAT)

        response = self.client.post('/api/v1/articles/%s/' % (model_data['id']), data=json.dumps(model_data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)

        model_data['date_updated'] = (datetime.utcnow() - timedelta(hours=2)).strftime(PARC_ISO_STRF_FORMAT)

        response = self.client.post('/api/v1/articles/%s/' % (model_data['id']), data=json.dumps(model_data),
                                    content_type='application/json')
        resp = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(resp['meta']['error_slug'], 'already-updated')


class TestAnnotations(MockModel, TestCase):
    def build_annotation(self):
        return {
            'quote': 'testing',
            'text': "text of the ",
            'ranges': [{
                'start': '/div',
                'startOffset': 10,
                'end': '/div',
                'endOffset': 0
            }]
        }

    def test_add_annotation(self):
        response = self.create_article()
        resp = json.loads(response.content)

        annotation = self.build_annotation()

        response = self.client.post('/api/v1/articles/%s/annotations/' % (resp['data']['id']), data=json.dumps(annotation),
                                    content_type='application/json')

        self.assertEqual(response.status_code, 200)

        resp = self.client.get('/api/v1/articles/%s/' % (resp['data']['id']), content_type='application/json')
        article_response = json.loads(resp.content)
        assert len(article_response['data']['annotations']) == 1

    def test_add_annotation_to_artcle(self):
        annotation = self.build_annotation()
        response = self.create_article(extra_data={
            'annotations': [annotation]
        })

        article_response = json.loads(response.content)

        article, _ = self.api_get('/api/v1/articles/%s/' % (article_response['data']['id']), content_type='application/json')
        assert len(article['annotations']) == 1

        annotation = self.build_annotation()
        article['annotations'] += [annotation]

        article['date_updated'] = (datetime.utcnow() + timedelta(hours=1)).strftime(PARC_ISO_STRF_FORMAT)
        self.api_post('/api/v1/articles/%s' % (article['id']), data=article, assert_status_code=200)

        article, _ = self.api_get('/api/v1/articles/%s/' % (article['id']))
        assert len(article['annotations']) == 2

        annotation = self.build_annotation()
        annotation['id'] = 34
        article['annotations'] += [annotation]

        article['date_updated'] = (datetime.utcnow() + timedelta(hours=2)).strftime(PARC_ISO_STRF_FORMAT)
        self.api_post('/api/v1/articles/%s' % (article['id']), data=article, assert_status_code=200)

        article, _ = self.api_get('/api/v1/articles/%s/' % (article['id']))
        assert len(article['annotations']) == 3

        annotation = self.build_annotation()
        annotation['id'] = article['annotations'][0]['id']
        article['annotations'] += [annotation]

        article['date_updated'] = (datetime.utcnow() + timedelta(hours=3)).strftime(PARC_ISO_STRF_FORMAT)
        self.api_post('/api/v1/articles/%s' % (article['id']), data=article, assert_status_code=200)

        article, _ = self.api_get('/api/v1/articles/%s/' % (article['id']))
        assert len(article['annotations']) == 3
