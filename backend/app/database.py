import sqlite3
import json
from datetime import datetime
from pathlib import Path


# Database file will be created inside backend/app/
DATABASE_PATH = Path(__file__).resolve().parent / "documents.db"


def get_connection():
    """Create and return a SQLite database connection."""
    return sqlite3.connect(DATABASE_PATH)


def init_db():
    """Create the documents table if it does not already exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_name TEXT NOT NULL,
            document_type TEXT NOT NULL,
            processing_status TEXT,
            extracted_data TEXT,
            validation TEXT,
            raw_text TEXT,
            processed_at TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_document(
    document_name,
    document_type,
    processing_status,
    extracted_data,
    validation,
    raw_text
):
    """Save a processed document and its results."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO documents (
            document_name,
            document_type,
            processing_status,
            extracted_data,
            validation,
            raw_text,
            processed_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        document_name,
        document_type,
        processing_status,
        json.dumps(extracted_data),
        json.dumps(validation),
        raw_text,
        datetime.now().isoformat()
    ))

    conn.commit()

    document_id = cursor.lastrowid

    conn.close()

    return document_id


def get_all_documents():
    """Return a list of all processed documents."""

    conn = get_connection()
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            document_name,
            document_type,
            processing_status,
            processed_at
        FROM documents
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]


def get_document_by_name(document_name):
    """Return complete details of a document by its name."""

    conn = get_connection()
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM documents
        WHERE document_name = ?
        ORDER BY id DESC
        LIMIT 1
    """, (document_name,))

    row = cursor.fetchone()

    conn.close()

    if row is None:
        return None

    result = dict(row)

    result["extracted_data"] = json.loads(
        result["extracted_data"]
    )

    result["validation"] = json.loads(
        result["validation"]
    )

    return result