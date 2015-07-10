from catalog.schemas import AnnotationSchema, RangeSchema

from .base import ParcApiObject


class RangeApiObject(ParcApiObject):
    schema = RangeSchema

    @classmethod
    def from_model(cls, model, *args, **kwargs):
        data = {
            'start': model.start,
            'startOffset': model.startOffset,
            'end': model.end,
            'endOffset': model.endOffset
        }

        return cls.get_schema()(data)


class AnnotationApiObject(ParcApiObject):
    schema = AnnotationSchema

    @classmethod
    def from_request(cls, request, *args, **kwargs):
        data = cls._parse_json_from_request(request, *args, **kwargs)
        obj = cls._deserialize(cls.get_schema(), data)

        return obj

    @classmethod
    def from_model(cls, model, *args, **kwargs):
        data = {
            'id': model.id,
            'quote': model.quote,
            'text': model.text,
            'date_saved': model.created,
            'date_updated': model.updated,
        }

        data['ranges'] = [RangeApiObject.from_model(range) for key, range in model.ranges.iteritems()]

        return cls.get_schema()(data)
