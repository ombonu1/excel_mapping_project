import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
import json
from google.adk.sessions import Session
from google.adk.tools import ToolContext
import re
from google.adk.events import Event, EventActions
import time
from google.api_core.exceptions import ServiceUnavailable, DeadlineExceeded, InternalServerError 
import traceback

# Import your agents
from process_mapping_agent.excel_understanding_agent import excel_understanding_agent
from process_mapping_agent.mapping_agent import process_visualization_agent as mapping_agent
from process_mapping_agent.sub_agents.product_selector_agent import product_selector_agent
from process_mapping_agent.sub_agents.feedback_agent import feedback_agent
from process_mapping_agent.sub_agents.final_output_agent import final_output_agent

from file_store import FILES

def clean_json_string(text):
    """Removes markdown code blocks and extra whitespace."""
    # Remove triple backticks and 'json' identifier
    text = re.sub(r'```(?:json)?', '', text)
    text = text.replace('```', '')
    return text.strip()

def extract_text_from_events(events):
    """
    Robustly extracts the last text response from a list of events.
    Skips over Function Calls and Tool Responses to find the actual LLM answer.
    """
    # Loop backwards (from newest to oldest)
    for event in reversed(events):
        try:
            # Check if the event has content
            if hasattr(event, 'content') and event.content:
                # Check parts
                if hasattr(event.content, 'parts'):
                    for part in event.content.parts:
                        # We found text! Return it immediately.
                        if hasattr(part, 'text') and part.text and part.text.strip():
                            return part.text
        except Exception:
            continue

    # Debugging: If no text found, print what we DID get (to help you troubleshoot)
    print("DEBUG: No text found. Event types received:")
    for e in events:
        print(type(e))
        
    raise ValueError("No text output found in agent response. The Agent might have called a tool but failed to generate a final summary.")

def json_safe(obj):
    if isinstance(obj, dict):
        return {k: json_safe(v) for k, v in obj.items()}

    if isinstance(obj, list):
        return [json_safe(v) for v in obj]

    if hasattr(obj, "isoformat"):
        # handles Timestamp, datetime, date
        return obj.isoformat()
    return obj



def run_with_retry(func, *args, retries=3, delay=2, **kwargs):
    """
    Robust execution wrapper. Retries on ANY crash.
    """
    last_exception = None
    
    for attempt in range(retries):
        try:
            return func(*args, **kwargs)
            
        except Exception as e:
            # We now catch EVERYTHING (Exception), not just specific ones.
            # This ensures 'AttributeError', 'RuntimeError', etc. are all retried.
            
            error_name = type(e).__name__
            print(f"⚠️ [Attempt {attempt+1}/{retries}] Hit error: {error_name} - {e}")
            
            # Specific check: If it's a fatal Auth error, don't retry (waste of time)
            if "PermissionDenied" in str(e) or "Unauthenticated" in str(e):
                raise e
            
            last_exception = e
            
            # Exponential backoff: Wait 2s, then 4s, then 6s
            sleep_time = delay * (attempt + 1)
            time.sleep(sleep_time)

    # If we get here, it's a persistent failure.
    print(f"❌ All {retries} retries failed.")
    print("Traceback of last error:")
    traceback.print_exc() # Print full details to console for debugging
    raise last_exception
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


def run_understanding_agent(uploaded_files):
    session_id = "default_session" 

    FILES[session_id] = {
        f.name: f.getvalue() for f in uploaded_files
    }
    
    file_names = list(FILES[session_id].keys())
    prompt = f"Please analyze these files: {file_names}. Call the specified metadata tool."

    # Simple run, no complex session injection needed
    def _attempt_run():
        events = asyncio.run(
            _understanding_runner.run_debug(prompt, session_id=session_id)
        ) 
        
        llm_text = extract_text_from_events(events)
        return json.loads(llm_text)
    return run_with_retry(_attempt_run, retries=3)

def run_product_selector_agent(understanding_json):
    # 1. Force conversion to String (Reliable!)
    # Whether it's the Mock Dict or real result, we turn it into a string.
    if isinstance(understanding_json, (dict, list)):
        json_str = json.dumps(understanding_json)
    else:
        json_str = understanding_json


    def _attempt_run():
        events = asyncio.run(
            _product_selector_runner.run_debug(
                json_str
            )
        )
        return extract_text_from_events(events)
    
    # 3. Extract text safely
    return run_with_retry(_attempt_run, retries=3)


def run_mapping_agent(understanding_json):
    # 1. Force conversion to String
    if isinstance(understanding_json, (dict, list)):
        json_str = json.dumps(understanding_json)
    else:
        json_str = understanding_json

    def _attempt_run():
        events = asyncio.run(
            _mapping_runner.run_debug(
                json_str
            )
        )

        return extract_text_from_events(events)
    
    return run_with_retry(_attempt_run, retries=3)


    # # 2. Inject into variable named "text" (or "understanding_json")
    # # We use "understanding_json" to be consistent with the Product Agent.
    # events = asyncio.run(
    #     _mapping_runner.run_debug(
    #         {"understanding_json": json_str}
    #     )
    # )

    # return extract_text_from_events(events)


# agent_runner.py

def run_feedback_agent(understanding_json, product_selection, user_feedback):
    """
    Runs the feedback loop. 
    NOTE: We replaced 'map_png_bytes' with 'product_selection' 
    because the agent needs the Tool Data, not the Image Pixels.
    """
    
    # 1. robustly parse inputs
    if isinstance(understanding_json, str):
        understanding_json = json.loads(understanding_json)
        
    if isinstance(product_selection, str):
        product_selection = json.loads(product_selection)

    # 2. Construct the Payload to match your PROMPT'S "INPUT FORMAT"
    # We use a placeholder for the path because the agent just needs to know one exists.
    payload = {
        "mapping_agent_output": {
            "process_map": understanding_json.get("process_map", []),
            "process_diagram_path": "process_map.png" 
        },
        "product_agent_output": product_selection,
        "user_feedback": user_feedback
    }

    # 3. Convert to String for the "Direct Message" pattern
    json_str = json.dumps(payload)

    # 4. Run the Agent
    def _attempt_run():
        events = asyncio.run(
            _feedback_runner.run_debug(json_str)
        )

        # 5. Use the SAFE extractor
        return extract_text_from_events(events)

    return run_with_retry(_attempt_run, retries=3)

def run_final_output_agent(understanding_json, product_selection, feedback):
    # 1. Structure the data to match your Agent Prompt's "INPUT CONTEXT"
    #    We assume the png is always at this standard path.
    payload = {
        "finalised_output": {
            "process_map": understanding_json.get("process_map", []),
            "recommended_tool": product_selection.get("recommended_tool", "Unknown"),
            "process_diagram_path": "process_map.png" 
        },
        "feedback_history": feedback
    }

    # 2. Create a NEW Runner instance locally.
    #    This ensures the agent starts with a blank memory slate every time you click the button.
    

    # 3. Send as a single JSON string.
    #    This prevents the "User > key" iteration issue.
    def _attempt_run():
        events = asyncio.run(
            _final_output_runner.run_debug(json.dumps(payload))
        )

        return extract_text_from_events(events)

    return run_with_retry(_attempt_run, retries=3)