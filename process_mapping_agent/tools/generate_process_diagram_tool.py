from graphviz import Digraph
import os

def generate_process_diagram_tool(process_data: dict) -> str:
    """
    Converts process dictionary into a Graphviz diagram and saves as PNG.
    Returns the absolute file path.
    """
    dot = Digraph(comment="Process Flow", format="png")
    dot.attr(rankdir="LR", size="8,5")

    for wb_id, wb in process_data.get("workbooks", {}).items():
        with dot.subgraph(name=f"cluster_{wb_id}") as wb_cluster:
            wb_cluster.attr(label=wb.get("name", wb_id), style="dashed")
            for sheet_id, sheet in wb.get("sheets", {}).items():
                with wb_cluster.subgraph(name=f"cluster_{wb_id}_{sheet_id}") as sheet_cluster:
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