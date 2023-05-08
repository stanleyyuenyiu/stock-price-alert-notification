from lib.database.client import DbClient
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import DuplicateColumnError, IntegrityError
from lib.utils.serializer import json_serialize_str

from . import entities, OutboxRepositoryImpl, OutboxServiceImpl, models

import logging
FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')


class SearchAlertOutboxService(OutboxServiceImpl):
    def __init__(self, repo:OutboxRepositoryImpl) -> None:
        self._repo = repo

    def save(self, model:models.Event):
        model.payload = json_serialize_str(model.payload)
        entity = entities.Outbox(**model.dict())
        return self._repo.save(entity)
      
    
    
        