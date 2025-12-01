import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
import json

# Import your agents
from process_mapping_agent.excel_understanding_agent import excel_understanding_agent
from process_mapping_agent.mapping_agent import process_visualization_agent as mapping_agent
from process_mapping_agent.sub_agents.product_selector_agent import product_selector_agent
from process_mapping_agent.sub_agents.feedback_agent import feedback_agent
from process_mapping_agent.sub_agents.final_output_agent import final_output_agent
from process_mapping_agent.tools.file_metadata_tool import build_files_metadata


def extract_text_from_events(events):
    """Safely extract LLM text from ADK event list."""
    for ev in reversed(events):  # search backwards for last usable event
        if ev.content and ev.content.parts:
            for p in ev.content.parts:
                if hasattr(p, "text") and p.text:
                    return p.text
    raise ValueError("No text output found in agent response.")

def json_safe(obj):
    if isinstance(obj, dict):
        return {k: json_safe(v) for k, v in obj.items()}

    if isinstance(obj, list):
        return [json_safe(v) for v in obj]

    if hasattr(obj, "isoformat"):
        # handles Timestamp, datetime, date
        return obj.isoformat()
    return obj


# ----------------------------------------------------------------------------
# Helper: create a Runner for each agent
# ----------------------------------------------------------------------------

def _make_runner(agent):
    session = InMemorySessionService()
    return Runner(
        agent=agent,
        app_name="ProcessDesignerApp",
        session_service=session
    )

_understanding_runner = _make_runner(excel_understanding_agent)
_mapping_runner = _make_runner(mapping_agent)
_product_selector_runner = _make_runner(product_selector_agent)
_feedback_runner = _make_runner(feedback_agent)
_final_output_runner = _make_runner(final_output_agent)


# ----------------------------------------------------------------------------
# RUN FUNCTIONS USED BY STREAMLIT
# ----------------------------------------------------------------------------

def extract_text_from_events(events):
   for ev in reversed(events):
       if ev.content and ev.content.parts:
           for part in ev.content.parts:
               if hasattr(part, "text") and part.text:
                   return part.text
   raise ValueError("No text output found in agent response.")
# The new simple runner:
def run_understanding_agent(uploaded_files):
   """
   uploaded_files: Streamlit list of UploadedFile objects
   This converts them to {name: bytes},
   builds metadata locally,
   JSON-safe converts,
   sends metadata JSON to the agent.
   """
   # 0️⃣ Convert Streamlit list → dict {filename: bytes}
   excel_files = {
       f.name: f.getvalue()
       for f in uploaded_files
   }
   # 1️⃣ Build metadata locally (NO tool calls)
   metadata = build_files_metadata(excel_files)
   # 2️⃣ Convert timestamps → JSON-safe
   safe_metadata = json_safe(metadata)
   message_json = json.dumps(safe_metadata, indent=2)
   # 3️⃣ Run the agent with JSON metadata
   events = asyncio.run(
       _understanding_runner.run_debug(message_json)
   )
   # 4️⃣ Extract final model text
   llm_text = extract_text_from_events(events)
   # 5️⃣ Parse JSON
   return json.loads(llm_text)


def run_mapping_agent(understanding_json):
    events = asyncio.run(_mapping_runner.run_debug({"text": json.dumps(understanding_json)}))
    return events[-1].content.parts[0].text


def run_product_selector_agent(understanding_json):
    events = asyncio.run(_product_selector_runner.run_debug({"understanding_json": understanding_json}))
    return events[-1].content.parts[0].text


def run_feedback_agent(understanding_json, map_png_bytes, user_feedback):
    events = asyncio.run(_feedback_runner.run_debug({
        "understanding_json": understanding_json,
        "map_png_bytes": map_png_bytes,
        "user_feedback": user_feedback
    }))
    return events[-1].content.parts[0].text


def run_final_output_agent(understanding_json, map_png_bytes, product_selection, feedback):
    events = asyncio.run(_final_output_runner.run_debug({
        "understanding_json": understanding_json,
        "map_png_bytes": map_png_bytes,
        "product_selection": product_selection,
        "feedback": feedback
    }))
    return events[-1].content.parts[0].text
