from typing import List, Generator
from elasticsearch import AsyncElasticsearch, NotFoundError
from elasticsearch.helpers import async_bulk, BulkIndexError
from .models import RuleModel, RuleDocModel, EnumOperator, EnumType, EnumUnit
from .helpers import to_model
from lib.database.decorators import transaction
from .repositories import RulesRepository
from .entities import RuleEntity
from lib.utils.hashing import object2hash

class NotFoundException(Exception):
    pass

class RuleESService():
    def __init__(self, 
        es_client:AsyncElasticsearch, 
        index:str,
    ) -> None:
        self._es_client = es_client
        self._index = index

    async def find(self, rule_id:str):
        doc = await self._es_client.get(
                index=self._index,
                id=rule_id
            )
            
        return to_model(doc)

    async def create_rule(self, rule:RuleModel):
        doc = self._init_doc(rule)
        return await self._es_client.create(index=self._index, id=rule.rule_id, body=doc)

    async def update_rule(self, rule:RuleModel):
        doc = self._build_update_doc(rule)
        return await self._es_client.update(index=self._index, id=rule.rule_id, body=doc)

    async def delete_rule(self, rule_id:str):
        return await self._es_client.delete(index=self._index, id=rule_id)

    async def delete_rules(self, rule_id:str):
        try:
            return await async_bulk(self._es_client, self._generate_delete_many_doc(rule_id))
        except BulkIndexError as e:
            for err in e.errors:
                if err["delete"]["result"] != "not_found":
                    raise
            

    async def inactive_rules(self, rules: List[RuleModel]):
        try:
            return await async_bulk(self._es_client, self._generate_inactive_query(rules))
        except BulkIndexError as e:
            for err in e.errors:
                print("ERROR", err["update"]["_id"])
            raise

    def _build_update_doc(self, rule:RuleModel) -> dict:
        return {
            "script": {
                "source": "def query = ctx._source.query; for (int i = 0; i < query.bool.must.size(); i++) { def must = query.bool.must[i];  if (must.range != null && must.range.containsKey('price')) {  must.range.price = params.new_price; }} ctx._source.alert_id = params.alert_id",
                "lang": "painless",
                "params": {
                    "new_price": {
                        rule.operator.value : rule.value
                    },
                    "alert_id": rule.alert_id
                }
            }
        }
         
    def _init_doc(self, rule:RuleModel) -> dict:
        _rule = {}
        _rule["price"] = {}
        _rule["price"][rule.operator.value] = self._build_price_doc(rule)
        return {
            
                "alert_id": rule.alert_id,
                "is_trigger" : False,
                "query" : {
                    "bool": {
                        "must": [
                            {
                                "range": _rule
                            },
                            {
                                "term": {
                                    "is_trigger" : False
                                }
                            },
                            {
                                "match": {
                                    "symbol": rule.symbol
                                }
                            }
                        ]
                    }
                }
         
        }
    
    def _build_price_doc(self, rule:RuleModel) -> float:
        if rule.unit == EnumUnit.NUMBER:
            return rule.value
        elif rule.unit == EnumUnit.PECENT:
            if rule.operator == EnumOperator.GTE:
                return rule.current + (rule.current * rule.value // 100)
            elif rule.operator == EnumOperator.LTE:
                return rule.current - (rule.current * rule.value // 100)

        raise Exception("Unknown rule unit")

    def _generate_inactive_many_doc(self, items: List[RuleModel]):
        for item in items:
            yield {
                "_op_type": "update",
                "_index": self._index,
                "_id": item.rule_id,
                "retry_on_conflict": 0,
                "script" : {
                    "source": "ctx._source.query.bool.must[1].term.is_trigger=params.value",
                    "lang": "painless",
                    "params": {
                        "value" : True
                    },
                }
            }

    def _generate_delete_many_doc(self, ids: List[str]):
        for id in ids:
            yield {
                "_op_type": "delete",
                "_index": self._index,
                "_id": id
            }

class RuleService():
    def __init__(self, 
        es_client:AsyncElasticsearch, 
        index:str,
        repo:RulesRepository
    ) -> None:
        self._es_client = es_client
        self._index = index
        self._repo = repo
        self._es = RuleESService(es_client, index)
        
    async def update_rule(self, item:RuleModel) -> bool:
        await self._update_rule(item) 

        await self._es.update_rule(item) 
    
    async def create_rule(self, item:RuleModel) -> RuleModel:
        id:str = object2hash(item.dict())

        item.rule_id = id
        
        await self._create_rule(item) 
        
        await self._es.create_rule(item) 
        
        return item
    
    async def delete_rule(self, id:str) -> bool:
        await self._delete_rule(id)

        try:
            await self._es.delete_rule(id)
        except NotFoundError as e:
            print(e)

    async def inactive_rules(self, ids:List[str]) -> bool:
        await self._inactive_rules(ids)

        ## it may fail when rules deleted in delete_rule
        await self._es.delete_rules(ids)

    @transaction
    async def _create_rule(self, item:RuleModel) :
        entity:RuleEntity = RuleEntity(**item.dict())
        self._repo.add(entity)

    @transaction
    async def _update_rule(self, item:RuleModel) :
        entity = RuleEntity(**item.dict())
        if not self._repo.update(entity):
            raise NotFoundException(f"Rule id {item.rule_id} not proceed") 
        return True

    @transaction
    async def _delete_rule(self, id:str):
        if not self._repo.delete(id):
            raise NotFoundException(f"Rule id {id} not proceed") 
        return True

    @transaction
    async def _inactive_rules(self, ids:List[str]):
        if not self._repo.inactive_many(ids):
            raise NotFoundException(f"Rule ids {ids} not proceed") 
        return True

    async def find_all(self, docs: List[RuleDocModel], size:int = 10000):
       pass
    
    @transaction
    async def find(self, id:str) -> RuleModel:
        model = RuleModel.from_orm(self._repo.get(id))
        if not model.rule_id:
            raise NotFoundException(f"Rule id {id} not found")
        return model

    async def search(self, docs: List[RuleDocModel], size:int = 10000):
        body = self._build_query(docs, size)
        resp = []
        start = True
        while start:
            start = False
            result = await self._es_client.search(
                index=self._index,
                filter_path=["hits.hits._id","hits.hits._source.alert_id", "hits.hits._source", "hits.total.value"],
                body=body
            )
            if "hits" in result:
                if "hits" in result["hits"]:
                    n = len(result["hits"]["hits"])
                    for doc in result["hits"]["hits"]:
                        model:RuleModel = to_model(doc)
                        resp.append(model)
                        
                    if n == size:
                        start = True
                        body["search_after"] = [model.alert_id]
       
        return resp
    
    def _build_query(self, docs: List[RuleDocModel], size: int = 10000) -> dict:
        documents: List[dict] = []
        
        for doc in docs:
            d:dict = doc.dict()
            d["price"] = d["value"]
            documents.append(d)
        
        query = {
            "percolate": {
                "field": "query",
                "documents": documents
            }
        }

        sort = {"alert_id": "asc"} ##timestamp + auto id + server id

        body = {
            "query": query,
            "sort": [sort],
            "size": size
        }

        return body