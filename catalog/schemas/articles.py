from schematics.types import StringType, URLType, BooleanType
from schematics.types.compound import ModelType, ListType


from .base import ParcSchema, ISODateTimeType, StringIntType
from .tags import TagSchema


class OriginSchema(ParcSchema):
    title = StringType()
    url = StringType()
    date_saved = ISODateTimeType()
    date_updated = ISODateTimeType()


class ArticleSchema(ParcSchema):
    id = StringIntType()
    url = URLType(required=True)
    title = StringType()
    html = StringType()
    date_saved = ISODateTimeType()
    date_updated = ISODateTimeType()
    origin = ModelType(OriginSchema)
    tags = ListType(ModelType(TagSchema))
    archived = BooleanType()
    deleted = BooleanType()
