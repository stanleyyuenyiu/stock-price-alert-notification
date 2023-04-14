from dependency_injector import containers, providers
from . import consumers

class ApplicationContainer(containers.DeclarativeContainer):

    kafka_client = providers.Dependency()

    rule_service = providers.Dependency()

    db_client = providers.Dependency()
    
    consumer = providers.Singleton(
        consumers.RemoveAlertConsumer,
        kafka_client=kafka_client,
        rule_service=rule_service
    )




