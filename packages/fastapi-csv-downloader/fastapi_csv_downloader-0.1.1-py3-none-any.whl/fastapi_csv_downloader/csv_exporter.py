import csv
import io
from fastapi import Response
from typing import List, Dict


def generate_csv_response(data: List[Dict], filename: str = "data.csv") -> Response:
    """
    Generate a CSV HTTP response from a list of dictionaries.

    Args:
        data (List[Dict]): List of records to write as CSV.
        filename (str): Name of the file to be downloaded.

    Returns:
        fastapi.Response: Response with CSV content and proper headers.
    """
    if not data:
        raise ValueError("Data list is empty. Cannot generate CSV.")

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
