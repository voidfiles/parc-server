from django.contrib import admin
from .models import Origin, Article, TaggedArticle, Tag, ImportJob


class OriginAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', )


class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'created', 'updated')


admin.site.register(Origin, OriginAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(TaggedArticle)
admin.site.register(Tag)
admin.site.register(ImportJob)
