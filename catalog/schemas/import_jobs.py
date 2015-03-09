from schematics.types import StringType, URLType, BooleanType

from .base import ParcSchema, ISODateTimeType, StringIntType


class ImportJobSchema(ParcSchema):
    id = StringIntType()
    job_reference = StringType()
    url = URLType(required=True)
    date_saved = ISODateTimeType()
    date_updated = ISODateTimeType()
    done = BooleanType()
    failed = BooleanType()
    running = BooleanType()
