from abc import ABC, abstractmethod
from models.entity import Base
from .models import Event

class OutboxRepositoryImpl(ABC):
    @abstractmethod
    def save(self, entities:Base):
        raise NotImplementedError

class OutboxServiceImpl(ABC):
    @abstractmethod
    def save(self, entities:Event):
        raise NotImplementedError
