# process_mapping_agent/tools/file_metadata_tool.py

import pandas as pd
from io import BytesIO

def build_files_metadata(uploaded_files):
    """
    uploaded_files can be either:
      - { filename: UploadedFileObject }
      - { filename: bytes }
    """
    files_list = []

    for filename, file_obj in uploaded_files.items():

        # --- Determine if the object is bytes or a Streamlit UploadedFile ---
        if hasattr(file_obj, "getvalue"):
            file_bytes = file_obj.getvalue()          # Streamlit mode
        else:
            file_bytes = file_obj                    # Test mode (bytes)

        buf = BytesIO(file_bytes)

        # --- Load Excel ---
        xls = pd.ExcelFile(buf, engine="openpyxl")

        sheet_infos = []
        for sheet in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet)

            sheet_infos.append({
                "sheet_name": sheet,
                "columns": df.columns.tolist(),
                "row_count": len(df),
                "sample_rows": df.head(5).to_dict(orient="records")
            })

        files_list.append({
            "file_name": filename,
            "sheets": sheet_infos
        })

    return {"files_metadata": {"files": files_list}}
