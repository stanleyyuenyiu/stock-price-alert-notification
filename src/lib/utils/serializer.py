import json
from abc import ABC, abstractmethod

def json_serialize_str( msg ):
    return json.dumps(msg)

def json_serialize( msg, s_obj):
    return json.dumps(msg).encode('utf-8')

