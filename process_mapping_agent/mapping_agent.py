# from google.adk import Tool, Context
import os
from graphviz import Digraph
from google.adk.models.google_llm import Gemini
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from google.genai import types
from process_mapping_agent.tools.generate_process_diagram_tool import generate_process_diagram_tool

generate_process_map_tool = FunctionTool(func=generate_process_diagram_tool)

retry_config = types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
)
print("Retries configured")

process_visualization_agent = LlmAgent(
    model=Gemini(model="gemini-2.5-flash", retry_options=retry_config),
    name="process_visualization_agent",
    description="Generates a process map PNG from the understanding JSON.",
    instruction="""
You are the Process Visualization Agent.

INPUT DATA
----------
The user will send you a message containing a **JSON string** describing a process.

YOUR TASK
---------
1. Parse the JSON from the user's message.
2. Extract the "process_map" list from it.
3. Call the tool `generate_process_map` using this data.

OUTPUT RULES
------------
- **Success:** If the tool works, your final answer should be the file path it returns (e.g., "process_map.png").
- **Failure:** If the string is invalid or the tool fails, please output a text error message explaining what went wrong. 

CRITICAL FINAL STEP:
3. After the tool runs, you MUST respond with the file path returned by the tool.
   - Do NOT just stop after calling the tool.
   - Your final output must be the file path string (e.g. "process_map.png").

Do not strictly return only the filename if there is an error; we need to know why it failed.
""",
    tools=[generate_process_map_tool],
)