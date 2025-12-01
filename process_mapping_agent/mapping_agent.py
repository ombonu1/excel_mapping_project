# from google.adk import Tool, Context
import os
from graphviz import Digraph
from google.adk.models.google_llm import Gemini
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from google.genai import types
from process_mapping_agent.utils import generate_process_map, create_json

generate_process_map_tool = FunctionTool(func=generate_process_map)

retry_config = types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
)
print("Retries configured")

process_visualization_agent = LlmAgent(
   model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
   name="process_visualization_agent",
   description="Takes an Understanding Agent JSON and generates a process map PNG.",
   instruction="""
You are the Process Visualization Agent.
INPUT YOU RECEIVE
-----------------
You will receive a SINGLE message whose `text` is a JSON object like:
{
 "process_map": [...],
 "issues": [...],
 "opportunities": [...]
}
This JSON already contains everything you need.
You MUST NOT ask the user to 'provide the JSON' again.
YOUR TASK
---------
1. Parse the JSON from the text message.
2. Extract the `process_map` field.
3. Call the tool `generate_process_map(process_data=...)` exactly once, passing the full JSON object or at least the process_map.
4. Return ONLY the tool's output (e.g. PNG file path or diagram code). Do not wrap it in extra explanation.
You must ALWAYS use the `generate_process_map` tool.
Do NOT chat or ask follow-up questions.
""",
   tools=[generate_process_map_tool],
)
