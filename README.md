# AI Document Extraction, Validation & API Platform

An AI-powered financial document processing platform that extracts meaningful information from financial documents, validates financial calculations, stores processed results, and provides structured JSON through REST APIs and a web dashboard.

## 1. Project Overview

The platform supports four financial document categories:

- Invoice
- Balance Sheet
- Profit & Loss
- Cash Flow Statement

Users can upload PDF, JPG, JPEG, and PNG documents through the web interface. The system validates the uploaded file, performs OCR-based text extraction, extracts structured financial information, performs financial validation checks, stores the result in SQLite, and displays the processed result through the dashboard.

## 2. Key Features

- PDF, JPG, JPEG and PNG document support
- File format and integrity validation
- Maximum PDF page validation
- OCR using Tesseract
- PDF processing using PyMuPDF
- Financial field extraction
- Support for four financial document types
- Financial formula validation
- PASS / FAIL / NOT_APPLICABLE validation status
- SQLite database persistence
- REST API using FastAPI
- Swagger API documentation
- Web-based upload interface
- Processed document dashboard
- Structured JSON response
- Raw OCR text availability
- Processing metadata and processing time

## 3. System Architecture

The architecture diagram is available at:

`docs/architecture.png`

Processing flow:

User
→ Frontend
→ FastAPI API
→ File Validation
→ OCR
→ Document Extraction
→ Financial Validation
→ SQLite Database
→ Structured JSON / Dashboard

## 4. Technology Stack

### Backend

- Python
- FastAPI
- Uvicorn
- PyMuPDF
- Tesseract OCR
- pytesseract
- Pillow
- SQLite

### Frontend

- HTML
- CSS
- JavaScript

### Development

- Visual Studio Code
- Python Virtual Environment
- Git / GitHub

## 5. Supported Documents

### Invoice

Extracts available invoice information such as:

- Invoice number
- Date
- Total amount
- Items when available

Validation includes checking whether an invoice total is available.

### Balance Sheet

Extracts financial information such as:

- Total assets
- Total liabilities
- Equity-related values
- Cash and cash equivalents when available

Validation:

`Total Assets = Total Liabilities`

### Profit & Loss

Extracts available values such as:

- Revenue / income
- Interest earned
- Other income
- Expenses
- Operating expenses
- Provisions
- Net profit

Validation:

`Total Income - Total Expenditure = Net Profit`

### Cash Flow Statement

Extracts available values such as:

- Cash from operating activities
- Cash from investing activities
- Cash from financing activities
- Net cash change
- Opening cash
- Closing cash

Validation:

`Opening Cash + Net Cash Change = Closing Cash`

## 6. Project Structure

```text
AI_Document_Platform/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── documents.db
│   │   └── services/
│   │       ├── invoice_parser.py
│   │       ├── ocr_service.py
│   │       └── validator.py
│   │
│   ├── requirements.txt
│   └── test_ocr.py
│
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
│
├── docs/
│   └── architecture.png
│
├── sample_outputs/
│   ├── invoice.json
│   ├── balance_sheet.json
│   ├── profit_and_loss.json
│   └── cash_flow_statement.json
│
├── .env.example
├── .gitignore
└── README.md