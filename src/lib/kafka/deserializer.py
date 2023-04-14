import json
from jsonschema import validate, ValidationError
from confluent_kafka.schema_registry.json_schema import JSONDeserializer as BaseJSONDeserializer
from confluent_kafka.serialization import SerializationError

class JSONDeserializer(BaseJSONDeserializer):
    def __call__(self, data, ctx):
        if data is None:
            return None
        
        payload = data.decode("utf-8")
        obj_dict = json.loads(payload)
     
        try:
            validate(instance=obj_dict, schema=self._parsed_schema)
        except ValidationError as ve:
            raise SerializationError(ve.message)
        
        if self._from_dict is not None:
            return self._from_dict(obj_dict, ctx)

        return obj_dict


