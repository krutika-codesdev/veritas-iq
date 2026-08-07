import pdfplumber


def extract_text_from_pdf(pdf_file):
    """
    Extract all text from an uploaded PDF.

    Parameters:
        pdf_file: Uploaded file object from Streamlit.

    Returns:
        str: Extracted text from all pages.
    """

    text = ""

    with pdfplumber.open(pdf_file) as pdf:

        for page in pdf.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    return text