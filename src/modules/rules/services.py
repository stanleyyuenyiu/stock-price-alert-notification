from typing import List, Generator
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk, BulkIndexError
from .models import RuleModel, RuleDocModel, EnumOperator

class RuleService():
    def __init__(self, es_client:AsyncElasticsearch, index:str) -> None:
        self._es_client = es_client
        self._index = index

    async def remove_many(self, items: List[RuleModel]):
        try:
            return await async_bulk(self._es_client, self.generate_delete_query(items))
        except BulkIndexError as e:
            for err in e.errors:
                print("ERROR", err["update"]["_id"])

    def generate_delete_query(self, items: List[RuleModel]):
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

    async def find_all(self, docs: List[RuleDocModel], size:int = 10000):
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
                        source_doc = doc["_source"]
                        
                        model = RuleModel(alert_id=source_doc["alert_id"], rule_id=doc["_id"])
                        for condition in source_doc["query"]["bool"]["must"]:
                            if "range" in condition and "price" in condition["range"]:
                                for operator in condition["range"]["price"]:
                                    model.operator = operator
                                    model.value = float(condition["range"]["price"][operator])
                            if "match" in condition and "symbol" in condition["match"]:
                                model.symbol = str(condition["match"]["symbol"])
                        
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