from abc import ABC, abstractmethod

class ConsumerListenerImp(ABC):
    @abstractmethod
    def __call__(self):
        raise NotImplementedError
