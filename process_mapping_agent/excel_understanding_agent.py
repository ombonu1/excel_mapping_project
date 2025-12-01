from google.adk import Agent

from config import DEFAULT_MODEL

from process_mapping_agent.schemas.excel_mapping_schema import UnderstandingAgentOutput

excel_understanding_agent = Agent(
    name="excel_understanding_agent",
    model=DEFAULT_MODEL,
    instruction="""

You are the Excel Understanding Agent.
You will receive pre-computed structured metadata:
{
  "files_metadata": {
      "files": [
          {
            "file_name": "...",

            "sheets": [

                {

                  "sheet_name": "...",

                  "columns": [...],

                  "row_count": 123,

                  "sample_rows": [...]

                }

            ]

          }

      ]

  }

}

Use ONLY this metadata to infer:

- the business process

- data relationships

- inefficiencies

- improvement opportunities

Return ONLY valid JSON following UnderstandingAgentOutput:

{

  "process_map": [ {"step_name": "...", "description": "..."} ],

  "issues": [...],

  "opportunities": [...]

}

""",

    output_schema=UnderstandingAgentOutput

)
 