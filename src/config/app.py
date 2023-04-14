from pydantic import BaseSettings
from functools import lru_cache
from typing import Optional
import os

class Settings(BaseSettings):
    salt: str

    class Config:
        path = os.path.realpath(os.path.dirname(__file__))
     
        env_file = f"{path}/../.app.env"
        env_file_encoding = 'utf-8'


settings = Settings()

@lru_cache()
def get_settings():
    return settings