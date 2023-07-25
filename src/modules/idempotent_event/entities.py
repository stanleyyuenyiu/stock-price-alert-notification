from lib.database.entities import Base
from sqlalchemy.schema import PrimaryKeyConstraint
from sqlalchemy import Column, String, Integer

class IdempotentEventEntity(Base):
    __tablename__ = "idempotent_event"
    event_id = Column(String, primary_key=True, index=True)
    group_id = Column(String, primary_key=True, index=True)


    __table_args__ = (
        PrimaryKeyConstraint(
            event_id,
            group_id),
        {})

    

