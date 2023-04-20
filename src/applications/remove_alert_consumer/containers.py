from dependency_injector import containers, providers, resources

from lib.kafka.client import KafkaClient, KafkaClientConfig
from lib.database.client import DbClient, DbClientConfig
from elasticsearch import AsyncElasticsearch

from config import get_settings
from modules.rules.containers import RulesContainer
from modules.idempotent_event.containers import ApplicationContainer as IdempotentEventContainer
from modules.remove_alert.containers import ApplicationContainer as RemoveAlertConsumerContainer

import logging
import sys

class ApplicationContainer(containers.DeclarativeContainer):
    config = providers.Configuration(pydantic_settings=[get_settings(configuration_file="alert_remove")])
    
    wiring_config = containers.WiringConfiguration(
        packages=[
            "lib.database",
            "lib.kafka"
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
    
    kafka_config_factory = providers.Factory(
        KafkaClientConfig,
        broker_uri=config.broker_config.broker_uri,
        consumer_group_id=config.broker_config.consumer_group_id,
        transaction_id=config.broker_config.transaction_id
    )

    kafka_client = providers.Singleton(
        KafkaClient,
        kafka_config_factory,
    )
    
    es_client = providers.Singleton(
        AsyncElasticsearch,
        config.es_config.es_host,
    )

    rule_module = providers.Container(
        RulesContainer,
        es_client=es_client,
        index=config.es_config.es_index
    )
    
    idempotent_event_module = providers.Container(
        IdempotentEventContainer,
        db_client=db_client
    )

    remove_alert_consumer_module = providers.Container(
        RemoveAlertConsumerContainer,
        rule_service=rule_module.rule_service,
        kafka_client=kafka_client,
        db_client=db_client
    )




