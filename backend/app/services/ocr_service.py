import os
import shutil
from pathlib import Path

import pymupdf
import pytesseract
from PIL import Image


# Tesseract configuration
# Works locally on Windows and can also work on
# Linux/cloud environments where Tesseract is installed.
WINDOWS_TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

if os.path.exists(WINDOWS_TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = WINDOWS_TESSERACT_PATH
else:
    tesseract_path = shutil.which("tesseract")

    if tesseract_path:
        pytesseract.pytesseract.tesseract_cmd = tesseract_path


def ocr_image(image: Image.Image) -> str:
    """
    Extract text from an image using Tesseract OCR.
    """

    image = image.convert("RGB")

    text = pytesseract.image_to_string(
        image,
        config="--psm 6"
    )

    return text.strip()


def ocr_pdf(pdf_path: str) -> str:
    """
    Convert each PDF page into an image and
    extract text using OCR.
    """

    document = pymupdf.open(pdf_path)

    all_text = []

    for page_number, page in enumerate(document, start=1):

        pixmap = page.get_pixmap(
            matrix=pymupdf.Matrix(2, 2)
        )

        image = Image.frombytes(
            "RGB",
            [pixmap.width, pixmap.height],
            pixmap.samples
        )

        page_text = ocr_image(image)

        all_text.append(
            f"\n--- PAGE {page_number} ---\n"
            f"{page_text}"
        )

    document.close()

    return "\n".join(all_text).strip()


def extract_text(file_path: str) -> str:
    """
    Extract text from PDF, JPG, JPEG or PNG files.
    """

    path = Path(file_path)
    extension = path.suffix.lower()

    if extension in [".jpg", ".jpeg", ".png"]:

        image = Image.open(file_path)

        return ocr_image(image)

    elif extension == ".pdf":

        return ocr_pdf(file_path)

    else:

        raise ValueError(
            "Unsupported file type. "
            "Only PDF, JPG, JPEG and PNG are allowed."
        )
