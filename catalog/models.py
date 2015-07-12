from urlparse import urlparse
import requests

from django.db import models, transaction
from taggit.managers import TaggableManager
from taggit.models import ItemBase, TagBase

from paucore.data.fields import (CreateDateTimeField, LastModifiedDateTimeField,
                                 DictField, Choices)
from paucore.data.pack2 import (Pack2, SinglePack2Container, PackField,
                                IntegerPackField, AutoIncrementDictPack2Container)
from paucore.utils.python import memoized_property

from .url_utils import canonicalize_url

from contextlib import contextmanager


class ParcManager(models.Manager):

    @contextmanager
    def edit(self, instance):
        with transaction.atomic():
                model_edit = self.get_queryset().select_for_update().get(pk=instance.pk)
                yield model_edit
                model_edit.save()


class Tag(TagBase):
    extra = DictField(default=dict)
    created = CreateDateTimeField()
    updated = LastModifiedDateTimeField()

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"


class TaggedArticle(ItemBase):
    tag = models.ForeignKey(Tag, related_name="%(app_label)s_%(class)s_items")
    content_object = models.ForeignKey('Article')
    extra = DictField(default=dict)
    created = CreateDateTimeField()
    updated = LastModifiedDateTimeField()

    @classmethod
    def tags_for(cls, model, instance=None):
        if instance is not None:
            return cls.tag_model().objects.filter(**{
                '%s__content_object' % cls.tag_relname(): instance
            })
        return cls.tag_model().objects.filter(**{
            '%s__content_object__isnull' % cls.tag_relname(): False
        }).distinct()


class Origin(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)
    url = models.CharField(max_length=255, null=True, blank=True, unique=True)
    created = CreateDateTimeField()
    updated = LastModifiedDateTimeField()
    extra = DictField(default=dict)


def normalise(output):
    if not output:
        return ''

    return output


class SocialDatum(dict):

    def __repr__(self):
        return normalise(self.get('og', self.get('twitter', '')))

    def __unicode__(self):
        return normalise(self.get('og', self.get('twitter', '')))

    @property
    def twitter(self):
        return normalise(self.get('twitter', ''))

    @property
    def open_graph(self):
        return normalise(self.get('og', ''))


class SocialData(Pack2):
    open_graph = PackField(key='o', docstring='Open Graph Meta Data', null_ok=True, default=lambda x: dict())
    twitter = PackField(key='t', docstring='Twitter Metadata', null_ok=True, default=lambda x: dict())

    def get_social_value(self, key):
        if self.open_graph and self.open_graph.get(key):
            return self.open_graph[key]

        if self.twitter and self.twitter.get(key):
            return self.twitter[key]

        return None

    @property
    def description(self):
        return self.get_social_value('description')

    @property
    def title(self):
        return self.get_social_value('title')


class ArticleInfo(Pack2):
    author = PackField(key='a', docstring='author info', null_ok=True)
    full_html = PackField(key='h', docstring='Full html of article', null_ok=True)
    full_text_html = PackField(key='t', docstring='Full html of main text in article', null_ok=True)


ARTICLE_STATUS = Choices(
    (1, 'UNREAD', 'Unread'),
    (2, 'ARCHIVED', 'Archived'),
    (10, 'DELETED', 'Deleted'),
)


class ArticleManger(ParcManager):
    def for_url(self, url):
        url = canonicalize_url(url)

        try:
            article = self.get(url=url)
        except self.model.DoesNotExist:
            return None, url

        return article, url

    def update_from_api_object(self, article, article_a):
        if article_a.deleted:
            article.status = ARTICLE_STATUS.DELETED
        elif article_a.archived:
            article.status = ARTICLE_STATUS.ARCHIVED

        article.save()

        return article

    def touch_article(self, article):
        with self.edit(article) as article_edit:
            pass

        return article_edit

    def bulk_Load_articles(self, articles):
        article_pks = [x.id for x in articles]
        annotations = Annotation.objects.filter(article_id__in=article_pks)

        for article in articles:
            article._cached_annotations = []

        articles_by_pk = {x.pk: x for x in articles}

        for annotation in annotations:
            articles_by_pk[annotation.article_id]._cached_annotations += [annotation]

        return articles


class Article(models.Model):
    title = models.TextField(max_length=1000, null=True, blank=True)
    url = models.CharField(max_length=255, null=True, blank=True, unique=True)
    processed = models.BooleanField(default=False)
    created = CreateDateTimeField()
    updated = LastModifiedDateTimeField()
    origin = models.ForeignKey(Origin, blank=True, null=True)
    extra = DictField(default=dict)
    status = models.IntegerField(choices=ARTICLE_STATUS, default=ARTICLE_STATUS.UNREAD)

    social_data = SinglePack2Container(pack_class=SocialData, field_name='extra', pack_key='s')
    article_info = SinglePack2Container(pack_class=ArticleInfo, field_name='extra', pack_key='a')

    tags = TaggableManager(through=TaggedArticle)
    objects = ArticleManger()

    def __repr__(self):
        return '<SiteArticle %r>' % (self.title,)

    @memoized_property()
    def annotations(self):
        return Annotation.objects.filter(article_id=self.pk)

    @property
    def domain(self):
        parts = urlparse(self.url)
        netloc = parts.netloc
        return netloc.replace('www.', '')

    @property
    def effective_title(self):
        social_title = self.social_data.title
        if social_title:
            return social_title

        return self.title

    @property
    def deleted(self):
        return self.status == ARTICLE_STATUS.DELETED

    @property
    def archived(self):
        return self.status == ARTICLE_STATUS.ARCHIVED


IMPORT_JOB_STATUS = Choices(
    (1, 'RUNNING', 'Running'),
    (2, 'DONE', 'Done'),
    (3, 'FAILED', 'Failed'),
)


class ImportJobManager(models.Manager):

    def create_from_api_object(self, api_obj):
        return self.create_from_url(api_obj.url)

    def create_from_url(self, source_url):
        resp = requests.get(source_url)
        resp.raise_for_status()

        return self.create_from_html(resp.content, source_url)

    def create_from_html(self, html, from_url=None):
        from integration.get_pocket import process_articles_delayed

        result = process_articles_delayed(html)

        import_job = self.model(celery_id=result.id)

        import_job.info.source_html = html
        if from_url:
            import_job.info.source_url = from_url

        import_job.save()

        return import_job

    def close_job(self, job):
        job.status = IMPORT_JOB_STATUS.DONE

        job.save()

        return job


class JobInfo(Pack2):
    source_url = PackField(key='s', docstring='Source URL', null_ok=True)
    source_html = PackField(key='h', docstring='Source HTML', null_ok=True)
    error_message = PackField(key='e', docstring='Reason Why Job Failed', null_ok=True)


class ImportJob(models.Model):
    celery_id = models.CharField(null=True, blank=True, max_length=255)
    created = CreateDateTimeField()
    updated = LastModifiedDateTimeField()
    extra = DictField(default=dict)
    status = models.IntegerField(choices=IMPORT_JOB_STATUS, default=IMPORT_JOB_STATUS.RUNNING)

    info = SinglePack2Container(pack_class=JobInfo, field_name='extra', pack_key='j')

    objects = ImportJobManager()

    def __repr__(self):
        return '<ImportJob %s %s>' % (self.info.source_url, self.created)

    def done(self):
        return self.status == IMPORT_JOB_STATUS.DONE

    def failed(self):
        return self.status == IMPORT_JOB_STATUS.FAILED

    def running(self):
        return self.status == IMPORT_JOB_STATUS.RUNNING


class AnnotationManager(ParcManager):

    def update_from_article_api_obj(self, article, article_api_obj):
        if not article_api_obj.annotations:
            return

        new_annotations = []
        annotations_with_ids = []

        for annotation in article_api_obj.annotations:
            annotation_id = annotation.get('id')
            if not annotation_id:
                new_annotations += [annotation]
            else:
                annotations_with_ids += [annotation]

        annotations_with_ids_by_id = {x.id: x for x in annotations_with_ids}

        annotations = self.filter(article=article).in_bulk(annotations_with_ids_by_id.keys())

        missing_ids = set(annotations_with_ids_by_id.keys()) - set(annotations.keys())

        for _id in missing_ids:
            new_annotations += [annotations_with_ids_by_id.get(_id)]

        created_annotations = []

        for annotation in new_annotations:
            created_annotations += [self.create_from_api_obj(article, annotation)]

        return created_annotations

    def create_from_api_obj(self, article, api_obj):
        annotation = self.model(article=article, quote=api_obj.get('quote'), text=api_obj.get('text'))
        annotation.save()

        with self.edit(annotation) as annotation_edit:
            for r in api_obj.get('ranges', []):
                idx, item = annotation_edit.ranges.new_item()
                for key in ('start', 'startOffset', 'end', 'endOffset'):
                    setattr(item, key, r.get(key))

        return annotation_edit


class Range(Pack2):
    start = PackField(key='s', docstring='start', null_ok=True)
    startOffset = IntegerPackField(key='so', docstring='startOffset', null_ok=True)
    end = PackField(key='e', docstring='e', null_ok=True)
    endOffset = IntegerPackField(key='eo', docstring='endOffset', null_ok=True)


class Annotation(models.Model):
    article = models.ForeignKey(Article)
    quote = models.TextField()
    text = models.TextField()

    ranges = AutoIncrementDictPack2Container(pack_class=Range, field_name='extra', pack_key='r')

    objects = AnnotationManager()
    created = CreateDateTimeField()
    updated = LastModifiedDateTimeField()
    extra = DictField(default=dict)
