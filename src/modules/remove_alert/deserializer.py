from lib.kafka.deserializer import JSONDeserializer
from typing import List
from modules.rules.models import RuleModel

class Deserializer(JSONDeserializer):
    def __init__(self, schema_str:str):
        super().__init__(schema_str, self.dict_to_list)

    def dict_to_list(self, obj, ctx) -> List[str]:
        if obj is None:
            return None
        
        if isinstance(obj["payload"], list):
            result = []
            for rule in obj["payload"]:
                result.append(RuleModel(**rule))
            return result
        else:
            raise Exception("undefined obj")