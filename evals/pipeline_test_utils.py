import json
import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

async def run_agent(agent, message):
    session = InMemorySessionService()
    runner = Runner(agent=agent, app_name="EvalApp", session_service=session)
    result = await runner.run_debug(json.dumps(message))
    return result

async def full_pipeline(
    excel_agent,
    mapping_agent,
    product_agent,
    feedback_agent,
    final_output_agent,
    excel_inputs,
    user_feedback_sequence
):

    # Step 1: Excel Understanding Agent
    excel_out = await run_agent(excel_agent, excel_inputs)

    # Step 2 + 3: parallel 
    mapping_out = await run_agent(mapping_agent, excel_out)
    product_out = await run_agent(product_agent, excel_out)
    current_output = {
        "initial_output": mapping_out,
        "product_selector_output": product_out,
        "png_path": mapping_out.get("png_path")
    }

    # Step 4: Feedback Loop
    prev_map = mapping_out.get("process_map")
    prev_png = mapping_out.get("png_path")

    for fb in user_feedback_sequence:
        payload = {
            "initial_output": current_output["initial_output"],
            "product_selector_output": current_output["product_selector_output"],
            "png_path": current_output["png_path"],
            "user_feedback": fb
        }
        step_out = await run_agent(feedback_agent, payload)
        current_output = {
            "initial_output": step_out,
            "product_selector_output": current_output["product_selector_output"],
            "png_path": step_out.get("updated_png_path"),
        }

        if step_out.get("user_satisfied"):
            break

    # Step 5: Final Output Agent

    final_payload = {
        "finalised_output": current_output["initial_output"]
    }

    final_output = await run_agent(final_output_agent, final_payload)
    return final_output
 