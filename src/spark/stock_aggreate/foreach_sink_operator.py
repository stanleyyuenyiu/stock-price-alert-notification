from abc import ABC, abstractmethod
class ForEachOperator(ABC):
    def open(self, partition_id, epoch_id):
        pass

    def process(self, row):
        pass

    def close(self, err):
        pass