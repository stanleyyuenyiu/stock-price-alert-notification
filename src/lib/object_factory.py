
import collections
import threading
from abc import ABC, abstractmethod
from lib.singleton import Singleton

class Builder(ABC):
    @abstractmethod
    def build(self, **kwargs):
        raise NotImplementedError

class SingletonBuilder(Builder):
    _instance = {}
    _lock = threading.Lock()

    def build(self, **kwargs):
        with self._lock:
                if not self._instance:
                    self._instance = self._build(**kwargs)
                return self._instance
    
    @abstractmethod
    def _build(self, **kwargs):
        raise NotImplementedError
        
class ObjectFactory:
    def __init__(self):
        self._builders = collections.defaultdict(Builder)

    def register_builder(self, key, builder:Builder):
        self._builders[key] = builder

    def create(self, key, **kwargs):
        builder = self._builders.get(key)
        if not builder:
            raise ValueError(key)
        return builder.build(**kwargs)
    
    def get(self, key, **kwargs):
        return self.create(key, **kwargs)

