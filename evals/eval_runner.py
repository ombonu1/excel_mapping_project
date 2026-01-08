import json
import asyncio
from pathlib import Path
from asserts import *
from pipeline_test_utils import full_pipeline, run_agent
from process_mapping_agent.excel_understanding_agent import excel_understanding_agent
from process_mapping_agent.mapping_agent import process_visualization_agent as mapping_agent
from process_mapping_agent.sub_agents.product_selector_agent import product_selector_agent
from process_mapping_agent.sub_agents.feedback_agent import feedback_agent
from process_mapping_agent.sub_agents.final_output_agent import final_output_agent

def load_eval_cases(folder):
    cases = []
    for f in Path(folder).glob("*.json"):
        with open(f, "r") as fh:
            cases.append(json.load(fh))
    return cases

async def feedback_loop_test(initial_inputs, feedback_sequence):
   """
   Runs the feedback agent repeatedly using a user feedback sequence.
   Each item in feedback_sequence represents one turn of feedback.
   """
   current_output = initial_inputs["initial_output"]
   product_selector_output = initial_inputs["product_selector_output"]
   for fb in feedback_sequence:
       # Prepare turn input
       loop_input = {
           "initial_output": current_output,
           "product_selector_output": product_selector_output,
           "user_feedback": fb
       }
       # Run feedback agent
       result = await run_agent(feedback_agent, loop_input)
       # The feedback agent returns updated structure
       current_output = {
           "process_map": result["updated_process_map"],
           "recommended_tool": result.get("updated_recommended_tool")
               or current_output["recommended_tool"],
           "reason_for_recommendation": result.get("reason_for_update")
       }
       # Early exit if user satisfied
       if result.get("user_satisfied") is True:
           return {
               "final_feedback_output": result,
               "iterations": len(feedback_sequence)
           }
   return {
       "final_feedback_output": result,
       "iterations": len(feedback_sequence)
   }

async def run_eval_case(case):
    inputs = case["input"]
    expected = case.get("expected", {})
    mode = case.get("mode", "single")   # "single" | "loop" | "pipeline"
    if mode == "single":
        agent = eval(case["agent"])   # yes, allowed
        result = await run_agent(agent, inputs)
        return {
            "case": case["name"],
            "passed": assert_value(result, expected["key"], expected["value"]),
            "output": result
        }
    elif mode == "loop":
        feedbacks = case["user_feedback"]
        result = await feedback_loop_test(inputs, feedbacks)
        return {"case": case["name"], "output": result}

    elif mode == "pipeline":
        result = await full_pipeline(
            excel_understanding_agent,
            mapping_agent,
            product_selector_agent,
            feedback_agent,
            final_output_agent,
            case["input"]["excel_inputs"],
            case["input"]["user_feedback_sequence"]
        )

        return {"case": case["name"], "output": result}

async def main():
    folders = [
        "cases/end_to_end/case_01_ms_automation.json",
        "cases/end_to_end/case_02_google_tabular.json",
        "cases/case_10_multistep_feedback.json",
        "cases/feedback_agent_loop/case_03_expand_step.json",
        "cases/case_04_change_to_allowed_tool.json",
        "cases/case_05_change_to_unsupported_tool.json",
        "cases/case_06_missing_fields.json",
        "cases/case_09_contradiction.json",
        "cases/case_07_empty_map.json",
        "cases/case_08_flowchart_validity.json"
        ]

    for folder in folders:
        print(f"\n=== RUNNING TESTS IN {folder} ===")
        cases = load_eval_cases(folder)
        for case in cases:
            result = await run_eval_case(case)
            print(result)

if __name__ == "__main__":
    asyncio.run(main())
 