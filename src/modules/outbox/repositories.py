from lib.database.client import DbClient
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import DuplicateColumnError, IntegrityError

from . import entities, OutboxRepositoryImpl

import logging
FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')


class SearchAlertRepository(OutboxRepositoryImpl):
    def __init__(self, db_client:DbClient) -> None:
        self._db = db_client

    def save(self, entity:entities.SearchAlertEntity):
        insert_stmt = insert(entities.SearchAlertEntity).values(
            key=entity.key,
            payload=entity.payload,
            created_at=entity.created_at,
            version=entity.version
        )
        upsert_do_nth_stmt = insert_stmt.on_conflict_do_nothing(
            index_elements=['key']
        )
        self._db.session.execute(upsert_do_nth_stmt)
      
    
    def get(self, id:str):
   
        pass
        