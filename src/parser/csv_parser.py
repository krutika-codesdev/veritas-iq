import csv


def extract_records_from_csv(csv_file):
    """
    Extract product records from an uploaded CSV file.

    Parameters:
        csv_file: Uploaded file object from Streamlit.

    Returns:
        list[dict]: Extracted CSV records.
    """

    records = []

    content = csv_file.read().decode("utf-8")

    reader = csv.DictReader(content.splitlines())

    for row in reader:
        records.append(dict(row))

    return records