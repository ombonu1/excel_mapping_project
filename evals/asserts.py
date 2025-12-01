import json
from pathlib import Path
def assert_schema(output, expected_schema):
   missing = []
   for key in expected_schema:
       if key not in output:
           missing.append(key)
   return missing  # empty list means OK
def assert_value(output, expected_key, expected_value):
   return output.get(expected_key) == expected_value
def assert_tool_in_top_5(output):
   if "recommended_tool" not in output:
       return False
   return output["recommended_tool"] in output.get("top_5_tools", [])
def assert_png_regenerated(prev_png, new_png, map_changed):
   if map_changed:
       return prev_png != new_png
   else:
       return prev_png == new_png
def assert_no_hallucinations(output, allowed_tools):
   tools = output.get("top_5_tools", [])
   return all(t in allowed_tools for t in tools)
def assert_process_map_structure(map_json):
   if not isinstance(map_json, list):
       return False
   for step in map_json:
       if not all(k in step for k in ["step_number", "step_name", "step_description"]):
           return False
   return True