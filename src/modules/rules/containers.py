from dependency_injector import containers, providers

from .services import RuleService
from .repositories import RulesRepository

class RulesContainer(containers.DeclarativeContainer):
    index = providers.Dependency()
    es_client = providers.Dependency()
    db_client = providers.Dependency()

    rule_repo = providers.Factory(
        RulesRepository,
        db_client=db_client
    )

    rule_service = providers.Factory(
        RuleService,
        es_client=es_client,
        index=index,
        repo=rule_repo
    )
