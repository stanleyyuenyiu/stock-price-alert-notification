from dependency_injector.wiring import Provide
from .containers import ApplicationContainer
from lib.consumer import ConsumerListenerImp

def create_app() -> ConsumerListenerImp:
    container = ApplicationContainer()
    return container.search_alert_consumer_module.consumer()

app = create_app()