from dependency_injector import containers, providers

from .services import RuleService, RuleSearchService
from .repositories import RulesRepository
from .consumer import RuleOutboxConsumer
from modules.outbox.repositories import OutboxRepository
class RulesContainer(containers.DeclarativeContainer):
    index = providers.Dependency()
    es_client = providers.Dependency()
    db_client = providers.Dependency()
    kafka_client = providers.Dependency()
    outbox_repo = providers.Factory(
        OutboxRepository,
        db_client=db_client,
        session_factory= db_client.provided.session,
    )

    rule_repo = providers.Factory(
        RulesRepository,
        db_client=db_client,
        session_factory= db_client.provided.session,
    )

    rule_service = providers.Factory(
        RuleService,
        es_client=es_client,
        index=index,
        repo=rule_repo,
        outbox_repo=outbox_repo
    )

    

    
