__all__ = ["QueryParamsDependency", "QueryParams", "SearchEngineDependency", "SearchEngine"]

from fastapi import Depends
from pymongo.collection import Collection
from pymongo.cursor import Cursor
from typing import Annotated, Literal
from dataclasses import dataclass

op_map = {
    ">=": "$gte",
    "<=": "$lte",
    "!=": "$ne",
    ">": "$gt",
    "<": "$lt",
    "=": "$eq",
    "~": "$regex",
}

def format_value(v: str, regex=False):
    return (
        int(v)
        if v.strip().isdigit()
        else float(v) if v.strip().isdecimal()
        else f"(?i){v.strip()}(?-i)" if regex
        else v.strip()
    )
    
def get_filter_query(filter_item: str):
    op = ""
    for o in op_map:
        if o in filter_item:
            op = o
            break
    if not op:
        return {}

    k, v = filter_item.split(op)
    return {k.strip(): {op_map[op]: format_value(v, regex=(op=="~"))}}

@dataclass
class QueryParams:
    filter: str = ""
    limit: int = 50
    offset: int = 0
    sort_by: str = "_id"
    sort_dir: Literal["asc", "desc"] = "asc"
    projection: str = ""
    
    def query_collection(self, collection: Collection) -> Cursor:
        filter_dict = {}
        filter_item_list = self.filter.split(",")

        for filter_item in filter_item_list:
            filter_dict.update(get_filter_query(filter_item))
        
        projection_dict = (
            {
                k.strip(): True if int(v) > 0 else False
                for k, v in map(lambda x: x.split("="), self.projection.split(","))
            }
            if self.projection
            else {}
        )
        
        return (
            collection.find(filter_dict, projection_dict)
            .limit(self.limit)
            .skip(self.offset)
            .sort(self.sort_by, 1 if self.sort_dir == "asc" else -1)
        )
        
    def aggregate_collection(self, collection: Collection) -> Cursor:
        pass    
        # TODO: Define custom MongoDB aggregation pipeline

@dataclass
class SearchEngine:
    query: str = "default query"
    param: str = "name"
    limit: int = 10
    
    def atlas_search(self, collection: Collection) -> Cursor:
        pipeline = [
            {
                "$search": {
                    "index": "searchProducts",
                    "text": {
                        "query": self.query,
                        "path": {
                            "wildcard": "*"
                        },
                        "fuzzy": {}
                    }
                }
            },
            {"$limit": self.limit}
        ]
        
        return collection.aggregate(pipeline)
    
    def autocomplete(self, collection: Collection) -> list[dict]:
        pipeline = [
            {
                "$search": {
                    "index": "autoCompleteProducts",
                    "autocomplete": {
                        "query": self.query,
                        "path": self.param,
                        "tokenOrder": "sequential"
                    }
                }
            },
            {"$limit": self.limit},
            {"$project": {self.param: 1}}  
        ]
        
        cursor = collection.aggregate(pipeline)   
        return [
            {
                "id": str(doc["_id"]),
                self.param: doc[self.param]
            }
            for doc in cursor
        ]
    

SearchEngineDependency = Annotated[SearchEngine, Depends()]
QueryParamsDependency = Annotated[QueryParams, Depends()]
