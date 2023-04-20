from .models import RuleModel, EnumOperator, EnumType, EnumUnit

def to_model(es_doc:dict):
    source_doc = es_doc["_source"]
    model = RuleModel(alert_id=source_doc["alert_id"], rule_id=es_doc["_id"])
    for condition in source_doc["query"]["bool"]["must"]:
        if "range" in condition and "price" in condition["range"]:
            for operator in condition["range"]["price"]:
                model.operator = EnumOperator(operator)
                model.value = float(condition["range"]["price"][operator])
        if "match" in condition and "symbol" in condition["match"]:
            model.symbol = str(condition["match"]["symbol"])
    return model