import hashlib
import pickle
from config import get_settings
import time
setting = get_settings(configuration_file="alert_search")

def consistent_hash(key:str, range:int=10):
    hash_int = int(sha256_hex_hash(key), 16)
    return (hash_int % range) 

def sha256_hex_hash(key:str):
    key_bytes = str(key+setting.salt).encode('utf-8')
    return hashlib.sha256(key_bytes).hexdigest()

def object2hash( object_dict: dict) -> str:
    encode = {
        "key": setting.salt,
        "nonce": time.monotonic_ns(),
        "data": object_dict
    }
    
    key_bytes = pickle.dumps(encode)

    return hashlib.sha256(key_bytes).hexdigest()