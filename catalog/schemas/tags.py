from schematics.types import StringType, IntType, DateTimeType

from .base import ParcSchema

PARC_ISO_STRF_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

def lower(value):
    if not value:
        return value

    return value.lower()


class TagSchema(ParcSchema):
    id = IntType()
    name = StringType(validators=[lower])
    slug = StringType()
    date_saved = DateTimeType(format=PARC_ISO_STRF_FORMAT, formats=PARC_ISO_STRF_FORMAT)
    date_updated = DateTimeType(format=PARC_ISO_STRF_FORMAT, formats=PARC_ISO_STRF_FORMAT)
