from sqlite3 import Timestamp
from lib.database.client import DbClient
from sqlalchemy import insert, update, delete, select, bindparam
from sqlalchemy.exc import DuplicateColumnError, IntegrityError
from lib.database import Repo
from lib.database.decorators import db_session
from lib.database.client import DbClient
from typing import List, Optional, Sequence, Callable, Iterator
from contextlib import AbstractContextManager
from sqlalchemy.orm import Session

from . import entities, OutboxRepositoryImpl
from .entities import Outbox
from .models import BaseEvent

import logging
FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')


class OutboxRepository(Repo, OutboxRepositoryImpl):
    def __init__(self, db_client:DbClient,  session_factory: Callable[..., AbstractContextManager[Session]]) -> None:
        self._db = db_client
        self._session_factory = session_factory
    
    @property
    def session_factory(self):
        return self._session_factory

    @db_session
    def save(self, model:BaseEvent, session:Session = None):
        insert_stmt = insert(Outbox).values(
            id = model.id,
            aggregatetype = model.aggregate_type,
            aggregateid = model.aggregate_id,
            type = model.type,
            payload = model.payload,
            timestamp = model.timestamp,
            version = model.version,
            partition = model.partition
        )
        # upsert_do_nth_stmt = insert_stmt.on_conflict_do_nothing(
        #     index_elements=['key']
        # )
        session.execute(insert_stmt)
      
    @db_session
    def get(self, id:str, session:Session = None) -> Outbox:
        stmt = (
            select(Outbox).
            where(Outbox.rule_id == id)
        )
        return session.execute(stmt).scalar()

        