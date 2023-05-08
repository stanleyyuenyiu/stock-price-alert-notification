from typing import Any
from dependency_injector.wiring import Provide, inject
from inspect import iscoroutinefunction
from sqlalchemy.orm import Session

from modules.outbox.models import BaseEvent
from . import Repo
from .client import DbClient

def transactional(f:callable):
    @inject
    async def async_wrapper(funcself:Any, *args, db_client:DbClient = Provide["db_client"]):
        with db_client.session() as session:
            with session.begin():
                return await f(funcself, *args)
           
    @inject
    def wrapper(funcself:Any, *args, db_client:DbClient = Provide["db_client"]):
        with db_client.session() as session:
            with session.begin():
                return f(funcself, *args)
    return async_wrapper if iscoroutinefunction(f) else wrapper

def db_session(f:callable):
    def wrapper(funcself:Any, *args , db_client:DbClient = Provide["db_client"]):
        if not isinstance(funcself, Repo):
            return f(funcself, *args)

        if db_client.has_session():
            return f(funcself, *args, db_client.get_session())
        else:
            with funcself.session_factory() as session:
                    return f(funcself, *args, session)
    return  wrapper

