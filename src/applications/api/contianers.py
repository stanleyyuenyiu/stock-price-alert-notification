from dependency_injector import containers, providers, resources

from lib.database.client import DbClient, DbClientConfig
from elasticsearch import AsyncElasticsearch

from config import get_settings
from modules.rules.containers import RulesContainer

import logging
import sys

class ApplicationContainer(containers.DeclarativeContainer):
    config = providers.Configuration(pydantic_settings=[get_settings(configuration_file="api")])

    wiring_config = containers.WiringConfiguration(
        packages=[
            "lib.database",
            "modules.rules"
        ]
    )

    logging_config = providers.Resource(
        logging.basicConfig,
        level=logging.DEBUG,
        format='%(asctime)s : %(message)s',
        stream=sys.stdout,
    )

    db_config_factory = providers.Factory(
        DbClientConfig,
        dsn=config.db_config.dsn
    )
 
    db_client = providers.Singleton(
        DbClient,
        db_config_factory,
    )
    
    es_client = providers.Singleton(
        AsyncElasticsearch,
        config.es_config.es_host,
    )

    rule_module = providers.Container(
        RulesContainer,
        es_client=es_client,
        db_client=db_client,
        index=config.es_config.es_index
    )
    

