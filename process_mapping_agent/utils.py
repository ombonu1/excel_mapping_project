import os
import json
from graphviz import Digraph

def generate_process_map(process_data: dict) -> str:
    """
    Converts process dictionary into a Graphviz diagram and saves as PNG.
    Returns the absolute file path.
    """
    dot = Digraph(comment="Process Flow", format="png")
    dot.attr(rankdir="LR", size="8,5")

     # The agent is passing a *string*, not a dict → fix it gracefully
    if isinstance(process_data, str):
       try:
           process_data = json.loads(process_data)
       except Exception:
           raise ValueError("generate_process_map: received a string but failed to decode JSON")

    for wb_id, wb in process_data.get("workbooks", {}).items():
        with dot.subgraph(name=f"cluster_{wb_id}") as wb_cluster:   # type:ignore
            wb_cluster.attr(label=wb.get("name", wb_id), style="dashed")
            for sheet_id, sheet in wb.get("sheets", {}).items():
                with wb_cluster.subgraph(name=f"cluster_{wb_id}_{sheet_id}") as sheet_cluster:  # type:ignore
                    sheet_cluster.attr(label=sheet.get("name", sheet_id), style="rounded")
                    for proc_id, proc in sheet.get("processes", {}).items():
                        for step_id, step in proc.get("steps", {}).items():
                            node_id = f"{wb_id}.{sheet_id}.{proc_id}.{step_id}"
                            label = step.get("name", step_id)
                            shape = step.get("visualization", {}).get("shape", "box")
                            color = step.get("visualization", {}).get("color", "lightblue")
                            sheet_cluster.node(node_id, label, shape=shape, style="filled", fillcolor=color)

                            for next_step in step.get("dependencies", {}).get("next_steps", []):
                                dot.edge(node_id, next_step)

    output_path = "process_map.png"
    try:
        dot.render(output_path, cleanup=True)
        return os.path.abspath(output_path)
    except Exception as e:
        return e

def create_json():
    example_process_data = {
    "workbooks": {
        "finance_wb": {
            "name": "Finance Workbook",
            "file_path": "finance.xlsx",
            "sheets": {
                "fixed_costs_sheet": {
                    "name": "Fixed Costs",
                    "description": "Contains monthly fixed cost data",
                    "processes": {
                        "fixed_cost_chart": {
                            "name": "Monthly Fixed Cost Line Chart",
                            "description": "Generates a line graph of monthly fixed costs",
                            "owner": "Finance Team",
                            "priority": "high",
                            "status": "active",
                            "steps": {
                                "step1": {
                                    "name": "Load Fixed Cost Data",
                                    "action_type": "data_entry",
                                    "input_sources": [{"type": "excel_cell", "reference": "A1:A12"}],
                                    "output_targets": [{"type": "dataframe", "reference": "fixed_cost_df"}],
                                    "dependencies": {"previous_steps": [], "next_steps": ["finance_wb.summary_sheet.step2"]},
                                    "frequency": "monthly",
                                    "conditions": {},
                                    "visualization": {"shape": "box", "color": "lightblue"}
                                }
                            }
                        }
                    }
                },
                "summary_sheet": {
                    "name": "Summary",
                    "description": "Aggregates data for visualization",
                    "processes": {
                        "fixed_cost_chart": {
                            "name": "Monthly Fixed Cost Line Chart",
                            "description": "Final chart generation",
                            "owner": "Finance Team",
                            "priority": "high",
                            "status": "active",
                            "steps": {
                                "step2": {
                                    "name": "Aggregate Fixed Costs",
                                    "action_type": "automated",
                                    "input_sources": [{"type": "dataframe", "reference": "fixed_cost_df"}],
                                    "output_targets": [{"type": "dataframe", "reference": "agg_fixed_cost_df"}],
                                    "dependencies": {"previous_steps": ["finance_wb.fixed_costs_sheet.step1"], "next_steps": ["finance_wb.summary_sheet.step3"]},
                                    "frequency": "monthly",
                                    "conditions": {},
                                    "visualization": {"shape": "ellipse", "color": "yellow"}
                                },
                                "step3": {
                                    "name": "Generate Line Chart",
                                    "action_type": "automated",
                                    "input_sources": [{"type": "dataframe", "reference": "agg_fixed_cost_df"}],
                                    "output_targets": [{"type": "chart", "reference": "fixed_cost_line_chart"}],
                                    "dependencies": {"previous_steps": ["finance_wb.summary_sheet.step2"], "next_steps": []},
                                    "frequency": "monthly",
                                    "conditions": {},
                                    "visualization": {"shape": "diamond", "color": "green"}
                                }
                            }
                        }
                    }
                }
            }
        },
        "hr_wb": {
            "name": "HR Workbook",
            "file_path": "hr.xlsx",
            "sheets": {
                "labour_costs_sheet": {
                    "name": "Labour Costs",
                    "description": "Contains monthly labour cost data",
                    "processes": {
                        "labour_cost_chart": {
                            "name": "Monthly Labour Cost Bar Chart",
                            "description": "Generates a bar chart of monthly labour costs",
                            "owner": "HR Team",
                            "priority": "medium",
                            "status": "active",
                            "steps": {
                                "step1": {
                                    "name": "Load Labour Cost Data",
                                    "action_type": "data_entry",
                                    "input_sources": [{"type": "excel_cell", "reference": "B1:B12"}],
                                    "output_targets": [{"type": "dataframe", "reference": "labour_cost_df"}],
                                    "dependencies": {"previous_steps": [], "next_steps": ["finance_wb.summary_sheet.step2"]},
                                    "frequency": "monthly",
                                    "conditions": {},
                                    "visualization": {"shape": "box", "color": "lightpink"}
                                }
                            }
                        }
                    }
                }}}}}
    json_input = json.dumps(example_process_data)
    return json_input