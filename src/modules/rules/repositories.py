from typing import List, Optional, Sequence, Callable, Iterator
from sqlalchemy import insert, update, delete, select, bindparam, ScalarResult
from sqlalchemy.orm import Session
from sqlalchemy.exc import DuplicateColumnError, IntegrityError
from sqlalchemy.sql.functions import count

from modules.rules.models import RuleModel
from .entities import RuleEntity
from contextlib import AbstractContextManager
from lib.database import Repo
from lib.database.decorators import db_session
from lib.database.client import DbClient

import logging
FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

class RulesRepository(Repo):
    def __init__(self, db_client:DbClient,  session_factory: Callable[..., AbstractContextManager[Session]]) -> None:
        self._db = db_client
        self._session_factory = session_factory
    
    @property
    def session_factory(self):
        return self._session_factory

    @db_session
    def add(self, model:RuleModel, session:Session = None) -> RuleModel:
        entity:RuleEntity = RuleEntity(**model.dict())
        session.add(entity)
        return model

    @db_session
    def update(self, model:RuleModel, session:Session = None) -> bool:
            stmt = (
                update(RuleEntity).
                where(RuleEntity.rule_id == model.rule_id).
                where(RuleEntity.is_trigger == False).
                values(
                    alert_id=model.alert_id,
                    type=model.type,
                    operator=model.operator,
                    unit=model.unit,
                    value=model.value,
                )
            )
            result = session.execute(stmt)
            return result.rowcount > 0

    @db_session
    def inactive(self, model:RuleModel, session:Session = None) -> bool:
        stmt = (
            update(RuleEntity).
            where(RuleEntity.rule_id == model.rule_id).
            values(
                is_trigger=True
            )
        )
        result = session.execute(stmt)
        return result.rowcount > 0
    
    @db_session
    def inactive_many(self, ids:List[str], session:Session = None) -> bool:
        stmt = (
            update(RuleEntity).
            where(RuleEntity.rule_id.in_(ids)).
            values(
                is_trigger=True
            )
        )
        result = session.connection().execute(stmt)
        return result.rowcount == len(ids)

    @db_session
    def get(self, id:str, session:Session = None) -> RuleEntity:
        stmt = (
            select(RuleEntity).
            where(RuleEntity.rule_id == id)
        )
        return RuleModel.from_orm(session.execute(stmt).scalar())

    @db_session
    def delete(self, id:str, session:Session = None) -> bool:
        stmt = (delete(RuleEntity) \
            .where(RuleEntity.rule_id == id) 
        )
        result = session.execute(stmt)
        return result.rowcount > 0
    
    @db_session
    def find_all_by_user(self, user_id, offset, size, session:Session = None) -> Sequence[RuleEntity]:
        stmt =  select(RuleEntity).where(RuleEntity.user_id == str(user_id)).offset(offset).limit(size)
        result = session.execute(stmt)
        return result.scalars().fetchall()

    @db_session
    def get_total_by_user(self, user_id, session:Session = None) -> int:
        stmt =  select(count("*")).where(RuleEntity.user_id == str(user_id))
        result = session.execute(stmt)
        return result.first().count

