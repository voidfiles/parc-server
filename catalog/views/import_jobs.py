from paucore.utils.python import cast_int
from simpleapi import api_export, SimpleHttpException

from catalog.objects import ImportJobApiObject
from catalog.models import ImportJob

from .utils import api_object_from_request, api_view

import_job_view = api_view(ImportJobApiObject)


@api_export(method='POST', path=r'import-jobs')
@import_job_view(collection=False)
def create_import_jobs(request):
    if 'multipart/form-data' in request.META['CONTENT_TYPE']:
        import_job = ImportJob.objects.create_from_html(request.FILES['attachment'].read())
    else:
        import_job_a = api_object_from_request(request, ImportJobApiObject)
        import_job = ImportJob.objects.create_from_api_object(import_job_a)

    return import_job


@api_export(method='GET', path=r'import-jobs')
@import_job_view(collection=True)
def get_import_jobs(request):
    return ImportJob.objects.all()


@api_export(method='GET', path=r'import-jobs/(?P<import_job_id>[0-9]+)')
@import_job_view(collection=False)
def get_import_job(request, import_job_id):
    import_job_id = cast_int(import_job_id, None)

    try:
        import_job = ImportJob.objects.get(id=import_job_id)
    except ImportJob.DoesNotExist:
        raise SimpleHttpException('Import Job with ID does not exsit', 'missing', code=404)

    return import_job


# @api_export(method='POST', path=r'articles/(?P<article_id>[0-9]+)')
# @import_job_view(collection=False)
# def alter_article(request, article_id):
#     article_id = cast_int(article_id, None)

#     try:
#         article = Article.objects.get(id=article_id)
#     except Article.DoesNotExist:
#         raise SimpleHttpException('Article with ID does not exsits', 'missing', code=404)

#     article_a = api_object_from_request(request, ArticleApiObject)

#     if article.updated > article_a.date_updated:
#         raise SimpleHttpException('Article on server has a more recent date_updated', 'already-updated', code=400)

#     article = Article.objects.update_from_api_object(article, article_a)

#     return article
