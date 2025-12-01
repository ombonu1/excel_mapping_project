import asyncio

import json

from google.adk.runners import Runner

from google.adk.sessions import InMemorySessionService

from product_selector_agent import product_selector_agent


# Create session store

session = InMemorySessionService()

# Create Runner

runner = Runner(

    agent=product_selector_agent,

    app_name="TestApp",

    session_service=session

)


# ------------------------------------------------------------

# DUMMY INPUT (realistic -> matches your upstream Excel outputs)

# ------------------------------------------------------------

DUMMY_INPUT = {

    "process_map": [

        {"step_number": 1, "step_name": "Extract Data", "step_description": "Load data from Excel sheets."},

        {"step_number": 2, "step_name": "Validate Entries", "step_description": "Ensure data meets quality rules."},

        {"step_number": 3, "step_name": "Approval Check", "step_description": "Manager reviews data exceptions."},

        {"step_number": 4, "step_name": "Upload", "step_description": "Publish validated dataset to SharePoint."}

    ],

    "extracted_features": {

        "process_type": "approval_flow",

        "task_volume": "high",

        "data_shape": "tabular",

        "requires_automation": True,

        "requires_approval_flow": True,

        "requires_data_validation": True,

        "dependencies_present": True,

        "looping_or_rework_detected": False,

        "manual_touchpoints_count": 6,

        "multi_department_process": True

    },

    "excel_analysis": {

        "excel_file_count": 5,

        "average_row_count": 7000,

        "columns_used": ["Employee", "Hours", "Status", "Manager", "Timestamp"],

        "formulas_detected": True,

        "lookup_patterns_detected": True,

        "data_quality_issues_detected": ["missing values", "duplicate rows"],

        "status_columns_detected": True,

        "date_fields_detected": True

    },

    "environment_context": {

        "inferred_preferred_stack": "Microsoft",

        "inferred_user_skill_level": "mixed",

        "inferred_governance_level": "strict",

        "integration_signals_detected": ["Outlook email", "SharePoint"]

    },

    "operational_context": {

        "team_size_estimate": "enterprise",

        "process_frequency": "weekly",

        "data_sensitivity": "medium"

    }

}


# ------------------------------------------------------------

# ASYNC TEST WRAPPER

# ------------------------------------------------------------

async def test_selector():

    print("\n=== TESTING PRODUCT SELECTOR AGENT ===\n")

    # ADK expects a JSON STRING, not a Python dict

    message = json.dumps(DUMMY_INPUT)

    output = await runner.run_debug(message)

    print("\n=== OUTPUT ===\n")

    print(output)


if __name__ == "__main__":

    asyncio.run(test_selector())
 