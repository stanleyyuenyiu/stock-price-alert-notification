from typing import List
from lib.database.client import DbClient
from sqlalchemy import insert, update, delete, select, bindparam
from sqlalchemy.exc import DuplicateColumnError, IntegrityError
from . import entities

import logging
FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')


class RulesRepository():
    def __init__(self, db_client:DbClient) -> None:
        self._db = db_client

    def add(self, entity:entities.RuleEntity) -> entities.RuleEntity:
        self._db.session.add(entity)
        return entity
            
    def update(self, entity:entities.RuleEntity) -> bool:
        stmt = (
            update(entities.RuleEntity).
            where(entities.RuleEntity.rule_id == entity.rule_id).
            where(entities.RuleEntity.is_trigger == True).
            values(
                alert_id=entity.alert_id,
                type=entity.type,
                operator=entity.operator,
                unit=entity.unit,
                value=entity.value,
            )
        )
        result = self._db.session.execute(stmt)
        return result.rowcount > 0
    
    def inactive(self, entity:entities.RuleEntity) -> bool:
        stmt = (
            update(entities.RuleEntity).
            where(entities.RuleEntity.rule_id == entity.rule_id).
            values(
                is_trigger=True
            )
        )
        result = self._db.session.execute(stmt)
        return result.rowcount > 0
    
    def inactive_many(self, ids:List[str]) -> bool:
        stmt = (
            update(entities.RuleEntity).
            where(entities.RuleEntity.rule_id == bindparam("id")).
            values(
                is_trigger=True
            )
        )
        result = self._db.session.connection().execute(stmt, [{"id": id} for id in ids])
        return result.rowcount == len(ids)

    def get(self, id:str) -> entities.RuleEntity:
        return self._db.session.query(entities.RuleEntity).get(id)

    def delete(self, id:str) -> bool:
        stmt = (delete(entities.RuleEntity) \
            .where(entities.RuleEntity.rule_id == id) 
        )
        result = self._db.session.execute(stmt)
        return result.rowcount > 0
    
    def list(self, **args) -> entities.RuleEntity:
        return self._db.session.query(entities.RuleEntity).where(
            **args
        )