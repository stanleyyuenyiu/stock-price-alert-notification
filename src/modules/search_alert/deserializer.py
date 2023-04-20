from lib.kafka.deserializer import JSONDeserializer
from .models import StockAggreateModel

class StockAggreateDeserializer(JSONDeserializer):
    def __init__(self, schema_str):
        super().__init__(schema_str, self.dict_to_object)

    def dict_to_object(self, obj, ctx):
        if obj is None:
            return None
        payload = obj['payload']
        return StockAggreateModel(
                symbol=payload['symbol'],
                min_price=payload['min_price'],
                max_price=payload['max_price'])
