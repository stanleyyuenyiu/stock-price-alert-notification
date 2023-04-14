from dependency_injector import containers, providers, resources
from . import repositories, services

class ApplicationContainer(containers.DeclarativeContainer):
    
    db_client = providers.Dependency()

    idempotent_event_repo = providers.Singleton(
        repositories.IdempotentEventRepository,
        db_client=db_client
    )

    idempotent_event_service = providers.Singleton(
        services.IdempotentEventService,
        repo=idempotent_event_repo
    )

