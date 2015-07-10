from schematics.types import StringType
from schematics.types.compound import ModelType, ListType


from .base import ParcSchema, ISODateTimeType, StringIntType


class RangeSchema(ParcSchema):
    start = StringType()
    startOffset = StringIntType()
    end = StringType()
    endOffset = StringIntType()


class AnnotationSchema(ParcSchema):
    id = StringIntType()
    quote = StringType()
    text = StringType()
    date_saved = ISODateTimeType()
    date_updated = ISODateTimeType()
    ranges = ListType(ModelType(RangeSchema))
