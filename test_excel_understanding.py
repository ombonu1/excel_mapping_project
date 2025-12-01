import asyncio

import json

from pathlib import Path

from google.adk.sessions import InMemorySessionService

from google.adk.runners import Runner

from process_mapping_agent.excel_understanding_agent import excel_understanding_agent

from process_mapping_agent.tools.file_metadata_tool import build_files_metadata

def json_safe(obj):

    if isinstance(obj, dict):

        return {k: json_safe(v) for k, v in obj.items()}

    if isinstance(obj, list):

        return [json_safe(v) for v in obj]

    if hasattr(obj, "isoformat"):

        # handles Timestamp, datetime, date

        return obj.isoformat()

    return obj


def extract_text_from_events(events):

    print("\n=== RAW EVENTS ===")

    for i, ev in enumerate(events):

        print(f"\n--- Event {i} ---")

        print(ev)

    for ev in reversed(events):

        if ev.content and ev.content.parts:

            for part in ev.content.parts:

                if hasattr(part, "text") and part.text:

                    print("\n=== FOUND MODEL TEXT ===")

                    print(part.text)

                    return part.text

    raise ValueError("No text output found in agent response.")


async def run_test(excel_path: str):

    file_path = Path(excel_path)

    if not file_path.exists():

        raise FileNotFoundError(f"File not found: {excel_path}")

    excel_bytes = file_path.read_bytes()

    # 1️⃣ Build metadata locally (no tools)

    excel_files = {file_path.name: excel_bytes}

    files_metadata = build_files_metadata(excel_files)

    print("\n=== FILES METADATA ===")

    safe_metadata = json_safe(files_metadata)

    message = (json.dumps(safe_metadata, indent=2))


    # 2️⃣ Setup ADK session + runner

    session = InMemorySessionService()

    runner = Runner(

        agent=excel_understanding_agent,

        app_name="excel_mapping_project",

        session_service=session,

    )

    print("\n=== RUNNING AGENT ===")

    events = await runner.run_debug(

        message

    )

    print("\n=== AGENT FINISHED ===")

    # 3️⃣ Extract model text

    output_text = extract_text_from_events(events)

    print("\n=== PARSED JSON OUTPUT ===")

    try:

        parsed = json.loads(output_text)

        print(json.dumps(parsed, indent=2))

    except Exception as e:

        print("⚠️ JSON parsing failed:", e)

        print("Raw output was:")

        print(output_text)


if __name__ == "__main__":

    asyncio.run(run_test("complex_finance_workbook.xlsx"))
 