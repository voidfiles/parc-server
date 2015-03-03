from schematics.types import StringType, IntType, DateTimeType

from .base import ParcSchema, PARC_ISO_STRF_FORMAT, PARC_ISO_STRF_FORMATS



def lower(value):
    if not value:
        return value

    return value.lower()


class TagSchema(ParcSchema):
    id = IntType()
    name = StringType(validators=[lower])
    slug = StringType()
    date_saved = DateTimeType(serialized_format=PARC_ISO_STRF_FORMAT, formats=PARC_ISO_STRF_FORMATS)
    date_updated = DateTimeType(serialized_format=PARC_ISO_STRF_FORMAT, formats=PARC_ISO_STRF_FORMATS)
