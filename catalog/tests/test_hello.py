import json

from django.test import TestCase


class TestHello(TestCase):
    def test_hello(self):

        response = self.client.get('/api/v1/hello', content_type='application/json')

        self.assertEqual(response.status_code, 200)
        resp = json.loads(response.content)

        self.assertEquals(resp['data'], "hello")
