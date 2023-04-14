import hashlib
import os
from abc import ABC, abstractmethod

class Queue(ABC):
    def consistent_hash(self, key:str, range:int=10):
        key_bytes = str(key).encode('utf-8')
        hash_value = hashlib.sha256(key_bytes).hexdigest()
        hash_int = int(hash_value, 16)
        return (hash_int % range) 

def load_msg_schema(schema:str):
    if not schema:
        raise Exception("schema is missing")
        
    path = os.path.realpath(os.path.dirname(__file__))
    schema_str = ''
    with open(f"{path}/../schema/json/{schema}") as f:
        schema_str = f.read()
    return schema_str