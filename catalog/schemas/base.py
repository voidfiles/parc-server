from schematics.models import Model

PARC_ISO_STRF_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
PARC_ISO_STRF_FORMATS = ('%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S')

class ParcSchema(Model):
    class Options:
        serialize_when_none = False
