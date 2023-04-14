from dependency_injector import containers, providers

from . import services


class RulesContainer(containers.DeclarativeContainer):
    index = providers.Dependency()
    es_client = providers.Dependency()

    rule_service = providers.Singleton(
        services.RuleService,
        es_client=es_client,
        index=index
    )
