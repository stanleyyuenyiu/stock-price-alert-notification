from lib.singleton import Singleton
from config import  DbConfig
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

import dataclasses

@dataclasses.dataclass
class DbClientConfig:
    dsn: str
    autoflush: bool = False
    autocommit: bool = False

class DbClient():
    session: Session
    def __init__(self, config:DbClientConfig) -> None:
        print("init DB client")
        engine = create_engine(
            config.dsn
        )
        self.session = sessionmaker(autocommit=config.autocommit, autoflush=config.autoflush, bind=engine)()
        
       