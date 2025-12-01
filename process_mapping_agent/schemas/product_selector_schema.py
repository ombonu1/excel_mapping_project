from pydantic import BaseModel
from typing import List

class ProductSelectorSchema(BaseModel):
   top_5_tools: List[str]
   recommended_tool: str
   reason_for_recommendation: str