from pydantic import BaseSettings
from functools import lru_cache
from typing import Optional
import os

class Settings(BaseSettings):
   
    broker_uri: str
    outbound_topic:str
    outbound_partition_range:int

    class Config:
        path = os.path.realpath(os.path.dirname(__file__))
        env_file = f"{path}/../.stock_generator.env"
        env_file_encoding = 'utf-8'


settings = Settings()

@lru_cache()
def get_settings():
    return settings