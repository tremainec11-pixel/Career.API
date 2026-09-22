from io import BytesIO

from pypdf import PdfReader


def extract_text_from_pdf(file_content: bytes) -> str:
    pdf_file = BytesIO(file_content)
    reader = PdfReader(pdf_file)

    extracted_text = []

    for page in reader.pages:
        text = page.extract_text()

        if text:
            extracted_text.append(text)

    return "\n".join(extracted_text).strip()