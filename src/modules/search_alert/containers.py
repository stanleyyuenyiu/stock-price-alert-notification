from dependency_injector import containers, providers, resources
from modules.outbox.containers import ApplicationContainer as OutboxContainer
from modules.idempotent_event.containers import ApplicationContainer as IdempotentEventContainer

from . import consumers,services

class ApplicationContainer(containers.DeclarativeContainer):
    
    db_client = providers.Dependency()

    kafka_client = providers.Dependency()

    rule_service = providers.Dependency()

    outbox_module = providers.Container(
        OutboxContainer,
        db_client=db_client
    )
    
    idempotent_event_module = providers.Container(
        IdempotentEventContainer,
        db_client=db_client
    )

    consumer = providers.Singleton(
        consumers.SearchAlertConsumer,
        kafka_client=kafka_client,
        rule_service=rule_service,
        outbox_service=outbox_module.outbox_search_alert_service,
        idempotent_service=idempotent_event_module.idempotent_event_service
    )




