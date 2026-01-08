# manual_tool_test.py
import os
import sys

# Add the project root to python path so imports work
sys.path.append(os.getcwd())

# Import your tool directly
from process_mapping_agent.tools.generate_process_diagram_tool import generate_process_diagram_tool

# The exact data structure your Understanding Agent outputs (A LIST of Dicts)
MOCK_DATA = [
    {"step_name": "Employee submits expense report", "description": "Fills template", "role": "Employee", "decision_point": False},
    {"step_name": "Manager reviews report", "description": "Checks receipts", "role": "Manager", "decision_point": True},
    {"step_name": "Finance final approval", "description": "Checks tax", "role": "Finance", "decision_point": False},
    {"step_name": "Payment processing", "description": "Manual entry", "role": "Finance", "decision_point": False}
]

print("--- STARTING LOCAL TOOL TEST ---")

# 1. Run the function
try:
    result_path = generate_process_diagram_tool(MOCK_DATA)
    print(f"✅ Tool executed successfully!")
    print(f"📍 Result Path: {result_path}")
    
    # 2. Verify the file exists
    if os.path.exists(result_path) and result_path.endswith('.png'):
        print(f"✅ File actually exists at {result_path}")
        print(f"📂 Size: {os.path.getsize(result_path)} bytes")
    else:
        print(f"❌ File missing or invalid extension.")

except Exception as e:
    print(f"❌ Tool crashed: {e}")