import datetime
import iso8601

from schematics.models import Model
from schematics.types import BaseType

PARC_ISO_STRF_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

class ParcSchema(Model):
    class Options:
        serialize_when_none = False



class ISODateTimeType(BaseType):
    MESSAGES = {
        'parse': u'Could not parse {0}. Should be ISO8601.',
    }


    def to_native(self, value, context=None):
        if isinstance(value, datetime.datetime):
            return value

        try:
            return iso8601.parse_date(value)
        except (ValueError, TypeError):
            pass

        raise ConversionError(self.messages['parse'].format(value))

    def to_primitive(self, value, context=None):
        return value.strftime(PARC_ISO_STRF_FORMAT)
