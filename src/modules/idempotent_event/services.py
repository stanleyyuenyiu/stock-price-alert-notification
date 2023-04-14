from lib.database.client import DbClient
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import DuplicateColumnError, IntegrityError
from psycopg2.errors import UniqueViolation
from lib.utils.serializer import json_serialize_str
from lib.database.decorators import transaction
from . import entities,  models, repositories
from exceptions.duplicate_event import DuplicateEventException
import logging
FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')


class IdempotentEventService():
    def __init__(self, repo:repositories.IdempotentEventRepository) -> None:
        self._repo = repo

    def save_and_flush(self, event_id:str):
        try:
            entity = entities.IdempotentEventEntity(event_id=event_id)
            return self._repo.save(entity)
        except UniqueViolation as e:
            raise DuplicateEventException(event_id=event_id, inner_exception=e);
        except IntegrityError as e:
            if type(e.orig) is UniqueViolation:
                raise DuplicateEventException(event_id=event_id, inner_exception=e);
        
        
        
      
    
    
        