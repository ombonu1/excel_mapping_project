from pydantic import BaseModel
from typing import List, Optional


class FlowchartNode(BaseModel):
    id: str
    label: str
    type: str 
    description: Optional[str]


class FlowchartEdge(BaseModel):
    from_: str  
    to: str
    label: Optional[str] = None


class ImplementationGuide(BaseModel):
    setup_steps: List[str]
    process_implementation_steps: List[str]
    tips_and_best_practices: List[str]


class RiskItem(BaseModel):
    risk: str
    mitigation: str


class FinalOutputSchema(BaseModel):
    flowchart: dict  # for use with lucidchart or similar potentially
    final_process_description: str
    selected_tool: str
    why_this_tool: str
    implementation_guide: ImplementationGuide
    assumptions: List[str]
    risks_and_mitigations: List[RiskItem]
    process_diagram_path: str
 