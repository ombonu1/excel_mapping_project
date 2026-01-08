from graphviz import Digraph
import os
from typing import List, Dict, Any

# NOTE: We use 'list' in the signature to satisfy the API Schema requirements.
# The internal code still handles Dicts safely.
def generate_process_diagram_tool(process_data: List[Dict[str, Any]]) -> str:
    """
    Generates a Graphviz PNG from the process_map list.
    Returns the absolute file path.
    """
    # 1. Normalize Data
    steps = []
    
    # Even though type hint says list, Python allows Dicts to pass at runtime.
    if isinstance(process_data, dict):
        steps = process_data.get("process_map", [])
        if not steps and "workbooks" in process_data:
             return "Error: Received old 'workbooks' format. Expected 'process_map' list."
             
    elif isinstance(process_data, list):
        steps = process_data
    
    if not steps:
        return "Error: No process steps found to visualize."

    # 2. Initialize Graphviz
    dot = Digraph(comment="Process Flow", format="png")
    dot.attr(rankdir="TB") 
    dot.attr('node', shape='box', style='filled', fillcolor='lightblue')

    # 3. Create Nodes
    for i, step in enumerate(steps):
        # Handle cases where step might be a string (rare but possible)
        if isinstance(step, str):
            step_name = step
            role = "Unknown"
            is_decision = False
        else:
            step_name = step.get("step_name", f"Step {i+1}")
            role = step.get("role", "Unknown Role")
            is_decision = step.get("decision_point", False)
        
        # Styling
        if is_decision:
            shape = "diamond"
            color = "orange"
        else:
            shape = "box"
            color = "lightblue"
            
        label = f"<{step_name}<BR/><FONT POINT-SIZE='10' COLOR='gray'>{role}</FONT>>"
        dot.node(str(i), label=label, shape=shape, fillcolor=color)

    # 4. Create Edges
    for i in range(len(steps) - 1):
        dot.edge(str(i), str(i+1))

    # 5. Render
    output_path = "process_map"
    try:
        full_path = dot.render(output_path, cleanup=True)
        return full_path
    except Exception as e:
        return f"Error rendering Graphviz: {str(e)}"