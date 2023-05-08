from lib.database.client import DbClient
from sqlalchemy import insert, update, delete, select, bindparam
from lib.database import Repo
from lib.database.decorators import db_session
from lib.database.client import DbClient
from typing import List, Optional, Sequence, Callable, Iterator
from contextlib import AbstractContextManager
from sqlalchemy.orm import Session

from .entities import IdempotentEventEntity
from .models import IdempotentEventModel
import logging
FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

class IdempotentEventRepository(Repo):
    def __init__(self, db_client:DbClient,  session_factory: Callable[..., AbstractContextManager[Session]]) -> None:
        self._db = db_client
        self._session_factory = session_factory

    @property
    def session_factory(self):
        return self._session_factory

    @db_session
    def save(self, model:IdempotentEventModel, session:Session = None):
        insert_stmt = insert(IdempotentEventEntity).values(
            event_id=model.event_id
        )
        session.execute(insert_stmt)
    
    @db_session
    def get(self, id:str, session:Session = None) -> IdempotentEventModel:
        stmt = (
            select(IdempotentEventEntity).
            where(IdempotentEventEntity.rule_id == id)
        )
        return IdempotentEventModel.from_orm(session.execute(stmt).scalar())
        