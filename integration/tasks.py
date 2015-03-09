from __future__ import absolute_import
import logging

from catalog.article import create_article_from_api_obj
from catalog.models import ImportJob

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def create_article_from_api_obj_delayed(self, api_obj, **kwargs):
    logger.info("Adding %s to list", api_obj.url)
    return create_article_from_api_obj(api_obj, **kwargs)


@shared_task(bind=True)
def close_import_job(self, *args, **kwargs):
    logger.info("Inside close import job %s", self.request)
    if hasattr(self.request, 'id'):
        try:
            import_job = ImportJob.objects.get(celery_id=self.request.id)
        except ImportJob.DoesNotExsist:
            return

        logger.info("Found import job %s", import_job)

        import_job = ImportJob.objects.close_job(import_job)
