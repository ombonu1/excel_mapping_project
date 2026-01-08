from typing import List, Optional
from pydantic import BaseModel, Field

class ProcessStep(BaseModel):
    # We already fixed this one
    step_number: Optional[int] = Field(default=None, description="The sequential number of the step")
    
    step_name: str = Field(description="The name of the process step")
    
    # --- CRITICAL FIXES BELOW ---
    # We add Optional[...] and default="..." to prevent crashes if the Agent forgets them.
    
    role: Optional[str] = Field(
        default="Unknown Role", 
        description="The role performing the step"
    )
    
    description: Optional[str] = Field(
        default="", 
        description="Details of the action taken"
    )
    
    decision_point: Optional[bool] = Field(
        default=False, 
        description="Is this a decision node?"
    )
    
    condition: Optional[str] = Field(
        default=None, 
        description="The condition logic if decision_point is True"
    )

# The rest of your file likely looks like this:
class FeedbackSchema(BaseModel):
    user_feedback: str
    agent_response_message: str = Field(
        description="A natural language response to the user. E.g., 'Great idea, I have removed that step.' or 'I cannot do that because...'"
    )
    changes_made: str
    updated_process_map: List[ProcessStep]
    updated_recommended_tool: Optional[str] = None
    updated_reason_for_tool: Optional[str] = None
    updated_process_diagram_path: Optional[str] = None
    reason_for_update: Optional[str] = None