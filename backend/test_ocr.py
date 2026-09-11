
from app.services.ocr_service import extract_text


# Put the path of your invoice JPG here
file_path = r"C:\Users\suma\Downloads\New Dataset 1\New Dataset\Invoices\20251118_000612.jpg"


try:
    # Extract text using OCR
    text = extract_text(file_path)

    print("\n" + "=" * 60)
    print("OCR OUTPUT")
    print("=" * 60)

    print(text)

    print("\n" + "=" * 60)
    print("OCR COMPLETED SUCCESSFULLY")
    print("=" * 60)

except Exception as e:
    print("\nOCR FAILED")
    print("Error:", str(e))