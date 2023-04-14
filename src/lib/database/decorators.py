from typing import Any
from dependency_injector.wiring import Provide, inject
from lib.database.client import DbClient
import functools
from inspect import iscoroutinefunction

def transaction(f:callable):

    @inject
    async def async_wrapper(funcself:Any, *args, db_client:DbClient = Provide["db_client"]):
        with db_client.session.begin():
            return await f(funcself, *args)

    @inject
    def wrapper(funcself:Any, *args, db_client:DbClient = Provide["db_client"]):
        with db_client.session.begin():
            return f(funcself, *args)

    return async_wrapper if iscoroutinefunction(f) else wrapper
    