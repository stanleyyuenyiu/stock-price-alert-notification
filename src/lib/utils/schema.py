import os
import json
def load_schema(schema:str):
    if not schema:
        raise Exception("schema is missing")
        
    path = os.path.realpath(os.path.dirname(__file__))
    schema_str = ''
    with open(f"{path}/../../schema/json/{schema}") as f:
        schema_str = f.read()
    return schema_str

def load_spark_schema(schema:str):
    if not schema:
        raise Exception("schema is missing")
        
    path = os.path.realpath(os.path.dirname(__file__))
    with open(f"{path}/../../schema/json/{schema}") as f:
        return json.load(f)