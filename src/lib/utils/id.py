import hashlib
import json
import pickle
from abc import ABC, abstractmethod

class HashId(ABC):
    def gen_hash_id(self, obj: object):
            return hashlib.sha256( pickle.dumps(obj.__dict__) ).hexdigest()

def gen_hash_id( obj: object) -> str:
    return hashlib.sha256( pickle.dumps(obj.__dict__) ).hexdigest()