from lib.database.entities import Base
from sqlalchemy import Column, String, Integer
from sqlalchemy.types import DateTime

class Outbox(Base):
    __tablename__ = "outbox"
    id = Column(String, primary_key=True, index=True)
    aggregatetype = Column(String, nullable=False)
    aggregateid = Column(String, nullable=False)
    type = Column(String, nullable=False)
    payload = Column(String, nullable=False)
    timestamp = Column(Integer(), nullable=False)
    version = Column(String, nullable=False)
    partition = Column(Integer(), nullable=False, default=0)
    

