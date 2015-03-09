import fileinput

from celery.result import AsyncResult
from django.core.management.base import BaseCommand
from catalog.models import ImportJob


def cb(*args, **kwargs):
    print "Response %s %s" % (args, kwargs)


class Command(BaseCommand):
    def handle(self, *args, **options):
        html = ''.join(x for x in fileinput.input(args))
        import_job = ImportJob.objects.create_from_html(html)
        result = AsyncResult(import_job.celery_id)
        result.get()
