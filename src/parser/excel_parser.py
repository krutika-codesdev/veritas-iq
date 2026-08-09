import pandas as pd


def extract_records_from_excel(excel_file):
    """
    Extract product records from an uploaded Excel file.

    Parameters:
        excel_file: Uploaded Excel file object or file path.

    Returns:
        list[dict]: Extracted Excel records.
    """

    dataframe = pd.read_excel(excel_file)

    records = dataframe.to_dict(orient="records")

    return records