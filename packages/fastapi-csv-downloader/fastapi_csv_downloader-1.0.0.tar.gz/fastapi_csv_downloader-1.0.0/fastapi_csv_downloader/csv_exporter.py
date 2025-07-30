import csv
import io
from typing import List, Dict
from fastapi.responses import StreamingResponse


def generate_csv_response(
    data: List[Dict], filename: str = "data.csv"
) -> StreamingResponse:
    """
    Generate a CSV HTTP response from a list of dictionaries.

    Args:
        data (List[Dict]): List of records to write as CSV.
        filename (str): Name of the file to be downloaded.

    Returns:
        fastapi.StreamingResponse: Response with CSV content and proper headers.
    """
    if not data:
        raise ValueError("Data list is empty. Cannot generate CSV.")

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
