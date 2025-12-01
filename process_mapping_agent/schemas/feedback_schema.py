from pydantic import BaseModel
from typing import List, Optional

class ProcessStep(BaseModel):
   step_number: int
   step_name: str
   step_description: str

class FeedbackSchema(BaseModel):
   user_feedback: str
   changes_made: str
   updated_process_map: List[ProcessStep]
   updated_recommended_tool: Optional[str]  # may be null when tool is invalid
   updated_process_diagram_path: Optional[str]  # NEW: path to regenerated PNG
   reason_for_update: str
   user_satisfied: bool