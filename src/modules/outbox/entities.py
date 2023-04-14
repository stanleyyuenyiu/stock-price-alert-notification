from lib.database.entities import Base
from sqlalchemy import Column, String, Integer

class SearchAlertEntity(Base):
    __tablename__ = "outbox_event_search_alert"
    key = Column(String, primary_key=True, index=True)
    payload = Column(String, nullable=False)
    created_at = Column(Integer, nullable=False)
    version = Column(String, nullable=False)
    

