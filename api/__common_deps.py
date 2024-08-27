__all__ = ["QueryParamsDependency", "QueryParams", "SearchEngineDependency", "SearchEngine"]

from dataclasses import dataclass
from typing import Annotated, Literal
from fastapi import Depends
from pymongo.collection import Collection
from pymongo.cursor import Cursor



@dataclass
class QueryParams:
    filter: str = ""
    gt: float = 0.0
    lt: float = float('inf')
    limit: int = 0
    offset: int = 0
    sort_by: str = "_id"
    sort_dir: Literal["asc", "desc"] = "asc"
    projection: str = ""
    
    def query_collection(self, collection: Collection) -> Cursor:
        filter_dict = (
            {
                k.strip(): (
                    int(v)
                    if v.strip().isdigit()
                    else float(v) if v.strip().isdecimal()
                    else {"$regex":f"(?i){v.strip()}(?-i)"}
                )
                for k, v in map(lambda x: x.split("="), self.filter.split(","))
            }
            if self.filter
            else {}
        )
        
        if "price" in filter_dict and (filter_dict["price"] == 0):
            filter_dict["price"] = {"$gte":self.gt,"$lte":self.lt}

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
    query: str = ""
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
    
    def autocomplete(self, collection: Collection) -> list[str]:
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
        return [doc[self.param] for doc in cursor]
    

SearchEngineDependency = Annotated[SearchEngine, Depends()]
QueryParamsDependency = Annotated[QueryParams, Depends()]
