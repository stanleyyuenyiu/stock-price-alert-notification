from lib.kafka.deserializer import JSONDeserializer
from .models import RuleModel,EnumType, EnumUnit, EnumOperator
from modules.outbox.models import Event
class Deserializer(JSONDeserializer):
    def __init__(self, schema_str):
        super().__init__(schema_str, self.dict_to_object)

    def dict_to_object(self, obj, ctx):
        if obj is None:
            return None
        
        payload_model = None

        if "payload" in obj:
            payload = obj["payload"]
            payload_model = RuleModel(
                value=payload['value'],
                current=payload['current'],
                is_trigger=payload['is_trigger'],
                symbol=payload['symbol'],
                alert_id=payload['alert_id'],
                user_id=payload['user_id'],
                rule_id=payload['rule_id'],
                type=EnumType(payload['type']),
                unit=EnumUnit(payload['unit']),
                operator=EnumOperator(payload['operator']),
            ) 

        return Event(
            key=obj["key"],
            payload=payload_model,
            created_at=obj["created_at"],
            version=obj["version"]
        ) 