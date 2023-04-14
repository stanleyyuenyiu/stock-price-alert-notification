from lib.database.entities import Base
from sqlalchemy import Column, String, Integer

class IdempotentEventEntity(Base):
    __tablename__ = "idempotent_event"
    event_id = Column(String, primary_key=True, index=True)
    

