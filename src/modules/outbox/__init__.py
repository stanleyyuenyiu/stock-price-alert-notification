from abc import ABC, abstractmethod
from .models import Event
class OutboxRepositoryImpl(ABC):
    @abstractmethod
    def save(self, entities:object):
        raise NotImplementedError

class OutboxServiceImpl(ABC):
    @abstractmethod
    def save(self, entities:Event):
        raise NotImplementedError
