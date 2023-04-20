
from fastapi import FastAPI
from .contianers import ApplicationContainer
from modules.rules import controllers as rule_controller

def create_app() -> FastAPI:
    container = ApplicationContainer()
    app = FastAPI()
    app.container = container
    app.include_router(rule_controller.router)
    return app

app = create_app()

