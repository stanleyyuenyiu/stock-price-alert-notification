import hashlib
import pickle
from config.app import get_settings
setting = get_settings()

def consistent_hash(key:str, range:int=10):
    hash_int = int(sha256_hex_hash(key), 16)
    return (hash_int % range) 

def sha256_hex_hash(key:str):
    key_bytes = str(key+setting.salt).encode('utf-8')
    return hashlib.sha256(key_bytes).hexdigest()

def object2hash( obj: object) -> str:
    key_bytes = str(obj.__dict__).encode('utf-8')
    return hashlib.sha256(key_bytes).hexdigest()