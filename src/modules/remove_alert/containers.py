from dependency_injector import containers, providers
from . import consumers

class ApplicationContainer(containers.DeclarativeContainer):

    rule_service = providers.Dependency()

    db_client = providers.Dependency()
    
    consumer = providers.Singleton(
        consumers.RemoveAlertConsumer,
        rule_service=rule_service
    )




