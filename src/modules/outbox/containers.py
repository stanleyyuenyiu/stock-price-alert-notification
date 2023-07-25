from dependency_injector import containers, providers, resources
from . import repositories, services

class ApplicationContainer(containers.DeclarativeContainer):
    
    db_client = providers.Dependency()

    outbox_search_alert_repo = providers.Singleton(
        repositories.OutboxRepository,
        db_client=db_client,
        session_factory= db_client.provided.session,
    )

    outbox_search_alert_service = providers.Singleton(
        services.SearchAlertOutboxService,
        repo=outbox_search_alert_repo
    )




