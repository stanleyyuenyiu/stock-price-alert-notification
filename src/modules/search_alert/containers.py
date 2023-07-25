from dependency_injector import containers, providers, resources
from modules.outbox.containers import ApplicationContainer as OutboxContainer
from modules.idempotent_event.containers import ApplicationContainer as IdempotentEventContainer
from modules.rules.containers import RulesContainer

from config import get_settings, Settings

from . import consumers,services

class ApplicationContainer(containers.DeclarativeContainer):
    config = providers.Configuration(pydantic_settings=[get_settings(configuration_file="alert_search")])

    db_client = providers.Dependency()
  
    kafka_client = providers.Dependency()

    es_client = providers.Dependency()

    outbox_module = providers.Container(
        OutboxContainer,
        db_client=db_client
    )
    
    idempotent_event_module = providers.Container(
        IdempotentEventContainer,
        db_client=db_client
    )

    rule_module = providers.Container(
        RulesContainer,
        es_client=es_client,
        db_client=db_client,
        kafka_client=kafka_client,
        index=config.es_config.es_index
    )

    consumer = providers.Singleton(
        consumers.SearchAlertConsumer,
        kafka_client=kafka_client,
        rule_service=rule_module.rule_service
    )




