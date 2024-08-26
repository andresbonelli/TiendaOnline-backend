__all__ = ["QueryParamsDependency", "QueryParams"]

from dataclasses import dataclass
from typing import Annotated, Literal
from collections import defaultdict
from pydantic import Field
from fastapi import Depends, Body
from pymongo.collection import Collection
from pymongo.cursor import Cursor



@dataclass
class QueryParams:
    filter: str = ""
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
                    else float(v) if v.strip().isdecimal() else {"$regex":f"(?i){v.strip()}(?-i)"}
                )
                for k, v in map(lambda x: x.split("="), self.filter.split(","))
            }
            if self.filter
            else {}
        )

        # WARNING: Note this return statement with parenthesis
        #          This is only to split the expression into more lines
        #          BUT BE CAUTIOUS, if you add a comma before de closing parenthesis
        #          it will become into a tuple and we don't want that.
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
  



QueryParamsDependency = Annotated[QueryParams, Depends()]
