from dependency_injector import containers, providers, resources

from lib.kafka.client import KafkaClient, KafkaClientConfig
from lib.database.client import DbClient, DbClientConfig
from elasticsearch import AsyncElasticsearch


from config import get_settings, Settings
from modules.rules.containers import RulesContainer
from modules.search_alert.containers import ApplicationContainer as SearchAlertConsumerContainer

import logging
import sys

class ApplicationContainer(containers.DeclarativeContainer):
    config = providers.Configuration(pydantic_settings=[get_settings(configuration_file="alert_search")])
   
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

    search_alert_consumer_module = providers.Container(
        SearchAlertConsumerContainer,
        rule_service=rule_module.rule_service,
        kafka_client=kafka_client,
        db_client=db_client
    )
    

    # kafka_module = providers.Container(
    #     KafkaContainer,
    #     kafka_client=kafka_client
    # )
    




