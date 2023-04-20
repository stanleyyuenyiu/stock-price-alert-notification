
from functools import lru_cache
from typing import Optional

from pydantic import (
    BaseSettings, 
    PostgresDsn,
    BaseModel,
    PostgresDsn
)
from functools import lru_cache
from typing import Optional


class DbConfig(BaseModel):
    dsn: PostgresDsn

class BrokerConfig(BaseModel):
    broker_uri: str
    inbound_topic:str
    inbound_partition:int
    outbound_topic:Optional[str]
    outbound_partition:Optional[int]
    consumer_group_id:str
    transaction_id:Optional[str]
    deserializer_schema:str

class EsConfig(BaseModel):
    es_host: str
    es_index: str

class Settings(BaseSettings):
    salt: str
    db_config: DbConfig
    broker_config: BrokerConfig
    es_config: EsConfig
    
    class Config:
        env_nested_delimiter = '.'
        # path = os.path.realpath(os.path.dirname(__file__))
        # env_file = f"{path}/../.env"
        env_file_encoding = 'utf-8'


@lru_cache
def get_settings(configuration_name:Optional[str] = "", configuration_file:Optional[str] = ""):

    if configuration_file:
        configuration_file = f".{configuration_file}.env"
    else:
        configuration_file = '.env'
        
    settings = Settings(_env_file=configuration_file)

    if configuration_name == '' :
        return settings
    if configuration_name  == "db_config":
        return settings.db_config
    if configuration_name  == "broker_config":
        return settings.broker_config
    if configuration_name  == "es_config":
        return settings.es_config
    if configuration_name  == "salt":
        return settings.salt
    raise Exception(f"Unknown configuration {configuration_name}")
