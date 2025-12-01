from pydantic import BaseModel
from typing import List, Dict, Any


class ProcessStep(BaseModel):
    step_name: str
    description: str


class UnderstandingAgentOutput(BaseModel):
    process_map: List[ProcessStep]
    issues: List[str]
    opportunities: List[str]
