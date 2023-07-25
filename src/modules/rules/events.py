from .models import RuleModel
from modules.outbox.models import BaseEvent

class AddEvent(BaseEvent):
    @classmethod
    def of(cls, model:RuleModel):
        return cls(id=model.rule_id, payload=model)

    @property
    def aggregate_type(self):
        return "Rule";
    
    @property
    def type(self):
        return "add";

class UpdateEvent(AddEvent):
    @property
    def type(self):
        return "update";

class DeleteEvent(AddEvent):
    @classmethod
    def of(cls, id):
        return cls(id=id, payload=None)

    @property
    def type(self):
        return "delete";

class TriggeEvent(AddEvent):
    @property
    def type(self):
        return "trigger";