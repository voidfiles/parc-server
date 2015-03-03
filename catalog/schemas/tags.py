from schematics.types import StringType, IntType, DateTimeType

from .base import ParcSchema, ISODateTimeType



def lower(value):
    if not value:
        return value

    return value.lower()


class TagSchema(ParcSchema):
    id = IntType()
    name = StringType(validators=[lower])
    slug = StringType()
    date_saved = ISODateTimeType()
    date_updated = ISODateTimeType()
