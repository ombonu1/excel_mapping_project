# from google.adk import Tool, Context
import os
from graphviz import Digraph
from google.adk.models.google_llm import Gemini
from google.adk.agents import LlmAgent
from google.genai import types
from process_mapping_agent.utils import generate_process_map, create_json

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
    description="An agent that takes a process dictionary and generates a process flow visualization.",
    instruction="""
    You are an AI agent responsible for creating process flow diagrams from structured process data.

    Steps:
    1. Accept a json or nested dictionary representing workbooks, sheets, processes, and steps.
    2. Use the visualization tool to convert this dictionary into a process map.
    3. Return the output as a file path or diagram code for embedding.

    Always use the visualization tool for rendering the process map.
    """,
    tools=[generate_process_map]
)
