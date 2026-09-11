import os
import tempfile
import time
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.services.ocr_service import extract_text
from app.services.invoice_parser import extract_invoice_fields
from app.services.validator import validate_invoice_data

from app.database import (
    init_db,
    save_document,
    get_all_documents,
    get_document_by_name
)


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="AI Document Extraction Platform",
    description=(
        "AI-powered financial document extraction, "
        "validation and storage platform."
    ),
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

init_db()


# ============================================================
# CONFIGURATION
# ============================================================

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png"
}

ALLOWED_DOCUMENT_TYPES = {
    "invoice",
    "balance_sheet",
    "profit_and_loss",
    "cash_flow_statement",
    "receipt"
}


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/api/v1/health")
def health_check():

    return {
        "status": "healthy",
        "service": "AI Document Extraction Platform",
        "timestamp": datetime.now().isoformat()
    }


# ============================================================
# PROCESS DOCUMENT
# ============================================================

@app.post("/api/v1/documents/process")
async def process_document(
    file: UploadFile = File(...),
    document_type: str = Form(...)
):

    start_time = time.time()

    # --------------------------------------------------------
    # Validate document type
    # --------------------------------------------------------

    document_type = document_type.strip().lower()

    if document_type not in ALLOWED_DOCUMENT_TYPES:

        raise HTTPException(
            status_code=400,
            detail={
                "error": "Unsupported document type.",
                "allowed_types": sorted(
                    list(ALLOWED_DOCUMENT_TYPES)
                )
            }
        )

    # --------------------------------------------------------
    # Validate filename
    # --------------------------------------------------------

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No file was provided."
        )

    extension = os.path.splitext(
        file.filename
    )[1].lower()

    # --------------------------------------------------------
    # Validate extension
    # --------------------------------------------------------

    if extension not in ALLOWED_EXTENSIONS:

        raise HTTPException(
            status_code=400,
            detail={
                "error": "Unsupported file format.",
                "supported_formats": sorted(
                    list(ALLOWED_EXTENSIONS)
                )
            }
        )

    temp_path = None

    try:

        # ====================================================
        # SAVE TEMPORARY FILE
        # ====================================================

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=extension
        ) as temp_file:

            temp_path = temp_file.name

            content = await file.read()

            if not content:

                raise HTTPException(
                    status_code=400,
                    detail="Uploaded file is empty."
                )

            temp_file.write(content)

        file_size = os.path.getsize(
            temp_path
        )

        # ====================================================
        # FILE VALIDATION
        # ====================================================

        file_validation = {
            "status": "PASS",
            "extension": extension,
            "file_size_bytes": file_size,
            "supported_format": True
        }

        # ====================================================
        # PDF PAGE VALIDATION
        # ====================================================

        if extension == ".pdf":

            try:

                import pymupdf

                pdf = pymupdf.open(
                    temp_path
                )

                page_count = pdf.page_count

                pdf.close()

                file_validation["page_count"] = (
                    page_count
                )

                if page_count == 0:

                    raise HTTPException(
                        status_code=400,
                        detail="PDF contains no pages."
                    )

                if page_count > 3:

                    raise HTTPException(
                        status_code=400,
                        detail=(
                            "PDF contains more than "
                            "3 pages. Maximum allowed "
                            "is 3 pages."
                        )
                    )

            except HTTPException:
                raise

            except Exception as e:

                raise HTTPException(
                    status_code=400,
                    detail={
                        "error":
                            "Invalid or corrupted PDF.",

                        "message":
                            str(e)
                    }
                )

        # ====================================================
        # OCR
        # ====================================================

        raw_text = extract_text(
            temp_path
        )

        if not raw_text or not raw_text.strip():

            raise HTTPException(
                status_code=422,
                detail=(
                    "No readable text could be extracted "
                    "from the document."
                )
            )

        # ====================================================
        # DATA EXTRACTION
        # ====================================================

        extracted_data = extract_invoice_fields(
            raw_text
        )

        # The document type is selected by the user
        # through the frontend/Swagger.

        extracted_data["document_type"] = (
            document_type
        )

        # ====================================================
        # FINANCIAL VALIDATION
        # ====================================================

        # IMPORTANT:
        # Use validate_invoice_data so the correct
        # validation is selected according to document type.

        validation = validate_invoice_data(
            extracted_data
        )

        # ====================================================
        # PROCESSING METADATA
        # ====================================================

        processing_time = (
            time.time() - start_time
        )

        processing_metadata = {

            "processed_at":
                datetime.now().isoformat(),

            "processing_time_seconds":
                processing_time,

            "file_size_bytes":
                file_size
        }

        # ====================================================
        # SAVE DOCUMENT TO SQLITE DATABASE
        # ====================================================

        document_id = save_document(

            document_name=file.filename,

            document_type=document_type,

            processing_status="SUCCESS",

            extracted_data=extracted_data,

            validation=validation,

            raw_text=raw_text
        )

        # ====================================================
        # FINAL RESPONSE
        # ====================================================

        return {

            "status":
                "SUCCESS",

            "document_id":
                document_id,

            "document_name":
                file.filename,

            "document_type":
                document_type,

            "file_validation":
                file_validation,

            "extracted_data":
                extracted_data,

            "validation":
                validation,

            "processing_metadata":
                processing_metadata,

            "raw_text":
                raw_text
        }

    # ========================================================
    # HTTP EXCEPTIONS
    # ========================================================

    except HTTPException:
        raise

    # ========================================================
    # GENERAL EXCEPTION HANDLING
    # ========================================================

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail={
                "error":
                    "Document processing failed.",

                "message":
                    str(e)
            }
        )

    # ========================================================
    # DELETE TEMPORARY FILE
    # ========================================================

    finally:

        if temp_path and os.path.exists(
            temp_path
        ):

            try:

                os.remove(
                    temp_path
                )

            except Exception:
                pass


# ============================================================
# LEGACY EXTRACTION ENDPOINT
# ============================================================

@app.post("/api/v1/extract")
async def extract_legacy(
    file: UploadFile = File(...)
):

    return await process_document(
        file=file,
        document_type="invoice"
    )


# ============================================================
# GET ALL PROCESSED DOCUMENTS
# ============================================================

@app.get("/api/v1/documents")
def list_documents():

    return {
        "status": "SUCCESS",
        "documents": get_all_documents()
    }


# ============================================================
# GET DOCUMENT BY NAME
# ============================================================

@app.get("/api/v1/documents/{document_name}")
def get_document(
    document_name: str
):

    document = get_document_by_name(
        document_name
    )

    if document is None:

        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    return {
        "status": "SUCCESS",
        "document": document
    }