import os
from pathlib import Path

import pymupdf
import pytesseract
from PIL import Image


# ---------------------------------------------------------
# TESSERACT OCR CONFIGURATION
# ---------------------------------------------------------

TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

if os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


# ---------------------------------------------------------
# OCR FOR IMAGE FILES
# ---------------------------------------------------------

def ocr_image(image: Image.Image) -> str:
    """
    Extract text from an image using Tesseract OCR.
    Supports JPG, JPEG and PNG images.
    """

    # Convert image to RGB
    image = image.convert("RGB")

    # Perform OCR
    text = pytesseract.image_to_string(
        image,
        config="--psm 6"
    )

    return text.strip()


# ---------------------------------------------------------
# OCR FOR PDF FILES
# ---------------------------------------------------------

def ocr_pdf(pdf_path: str) -> str:
    """
    Convert each PDF page into an image
    and perform OCR on every page.
    """

    document = pymupdf.open(pdf_path)

    all_text = []

    for page_number, page in enumerate(document, start=1):

        # Render PDF page at higher resolution
        pixmap = page.get_pixmap(
            matrix=pymupdf.Matrix(2, 2)
        )

        # Convert PDF page to PIL image
        image = Image.frombytes(
            "RGB",
            [pixmap.width, pixmap.height],
            pixmap.samples
        )

        # OCR the page
        page_text = ocr_image(image)

        # Keep page information
        all_text.append(
            f"\n--- PAGE {page_number} ---\n"
            f"{page_text}"
        )

    document.close()

    return "\n".join(all_text).strip()


# ---------------------------------------------------------
# MAIN TEXT EXTRACTION FUNCTION
# ---------------------------------------------------------

def extract_text(file_path: str) -> str:
    """
    Detect the uploaded file type and perform OCR.

    Supported:
        PDF
        JPG
        JPEG
        PNG
    """

    path = Path(file_path)

    extension = path.suffix.lower()

    # Image documents
    if extension in [".jpg", ".jpeg", ".png"]:

        image = Image.open(file_path)

        return ocr_image(image)

    # PDF documents
    elif extension == ".pdf":

        return ocr_pdf(file_path)

    # Unsupported file
    else:

        raise ValueError(
            "Unsupported file type. "
            "Only PDF, JPG, JPEG and PNG are allowed."
        )