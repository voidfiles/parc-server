from django.test import TestCase
import json
import os
import vcr

from catalog.models import ImportJob

BASE_DIR = os.path.dirname(__file__) + '/data/'

RIL_IMPORT_HTML = ''
with open(BASE_DIR + 'ril_import.html') as fd:
    RIL_IMPORT_HTML = fd.read()

CASSETTE_DIR = BASE_DIR + '/cassettes/'

my_vcr = vcr.VCR(
    cassette_library_dir=CASSETTE_DIR,
    record_mode='once',
)


class TestImportJob(TestCase):
    def test_import_job_from_file(self):
        with open(BASE_DIR + 'ril_import.html') as fp:
            response = self.client.post('/api/v1/import-jobs', {
                'name': 'fred',
                'attachment': fp
            })

        resp = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        assert 'id' in resp['data']

        job = ImportJob.objects.get(celery_id=resp['data']['job_reference'])

        self.assertEquals(str(job.id), resp['data']['id'])

    def test_import_job_from_url(self):
        with my_vcr.use_cassette('test_import_job_from_url.json'):
            response = self.client.post('/api/v1/import-jobs', json.dumps({
                'url': ('https://gist.githubusercontent.com/voidfiles/eed96426493c148caa8c/'
                        'raw/2e742622f1538b8f9f60abdad09f1e337bf41e68/some.html')
            }), content_type='application/json')

        resp = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        assert 'id' in resp['data']

        job = ImportJob.objects.get(celery_id=resp['data']['job_reference'])

        self.assertEquals(str(job.id), resp['data']['id'])
