from .base import ParcApiObject

from catalog.schemas import ImportJobSchema


class ImportJobApiObject(ParcApiObject):
    schema = ImportJobSchema

    @classmethod
    def from_request(cls, request, *args, **kwargs):
        data = cls._parse_json_from_request(request, *args, **kwargs)
        obj = cls._deserialize(cls.get_schema(), data)

        return obj

    @classmethod
    def from_model(cls, model, *args, **kwargs):

        data = {
            'id': model.id,
            'job_reference': model.celery_id,
            'date_saved': model.created,
            'date_updated': model.updated,
            'done': model.done(),
            'failed': model.failed(),
            'running': model.running(),
        }

        return cls.get_schema()(data)
