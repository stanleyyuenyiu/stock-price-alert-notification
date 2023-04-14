from dependency_injector.wiring import Provide
from .containers import ApplicationContainer
from lib.consumer import ConsumerListenerImp

async def App(
    consumer:ConsumerListenerImp = Provide(ApplicationContainer.search_alert_consumer_module.consumer)
):
    await consumer()

container = ApplicationContainer()
container.init_resources()
container.wire(
    modules=[
        __name__, 
    ],
    packages=[
        "lib.database",
        "lib.kafka"
    ],
)
