from lib.database.client import DbClient
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import DuplicateColumnError, IntegrityError
from . import entities

import logging
FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

class IdempotentEventRepository():
    def __init__(self, db_client:DbClient) -> None:
        self._db = db_client

    def save(self, entity:entities.IdempotentEventEntity):
        insert_stmt = insert(entities.IdempotentEventEntity).values(
            event_id=entity.event_id
        )
        self._db.session.execute(insert_stmt)
      
    
    def get(self, id:str):
        pass
        