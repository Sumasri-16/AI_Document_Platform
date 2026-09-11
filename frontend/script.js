const API_BASE = "https://ai-document-platform-k3k2.onrender.com/api/v1";


// =====================================================
// API HEALTH CHECK
// =====================================================

async function checkHealth() {

    const statusText = document.getElementById("statusText");
    const statusDot = document.getElementById("statusDot");

    try {

        const response = await fetch(`${API_BASE}/health`);

        if (!response.ok) {
            throw new Error("API unavailable");
        }

        statusText.textContent = "API Online";
        statusDot.classList.add("online");

    } catch (error) {

        statusText.textContent = "API Offline";
        statusDot.classList.remove("online");

    }
}


// =====================================================
// PROCESS DOCUMENT
// =====================================================

async function processDocument() {

    const fileInput = document.getElementById("fileInput");
    const documentType = document.getElementById("documentType");
    const processBtn = document.getElementById("processBtn");
    const message = document.getElementById("message");

    // Check document type
    if (!documentType.value) {

        message.textContent =
            "Please select a document type.";

        return;
    }

    // Check file
    if (!fileInput.files.length) {

        message.textContent =
            "Please select a document.";

        return;
    }

    const file = fileInput.files[0];

    // Create form data
    const formData = new FormData();

    formData.append("file", file);
    formData.append("document_type", documentType.value);

    // Disable button while processing
    processBtn.disabled = true;
    processBtn.textContent = "Processing...";

    message.textContent =
        "Extracting document. Please wait...";

    try {

        const response = await fetch(
            `${API_BASE}/documents/process`,
            {
                method: "POST",
                body: formData
            }
        );

        const data = await response.json();

        // Handle API errors
        if (!response.ok) {

            throw new Error(
                data.detail?.error ||
                data.detail ||
                "Document processing failed."
            );
        }

        // Display result
        displayResult(data);

        message.textContent =
            "Document processed successfully.";

        // Refresh dashboard
        loadDocuments();

    } catch (error) {

        console.error("Processing error:", error);

        message.textContent =
            "Error: " + error.message;

    } finally {

        processBtn.disabled = false;
        processBtn.textContent =
            "Extract & Process";
    }
}


// =====================================================
// DISPLAY EXTRACTION RESULT
// =====================================================

function displayResult(data) {

    const resultSection =
        document.getElementById("resultSection");

    resultSection.style.display = "block";


    // -------------------------------------------------
    // DOCUMENT NAME
    // -------------------------------------------------

    document.getElementById("resultDocument").textContent =
        data.document_name ||
        data.filename ||
        "-";


    // -------------------------------------------------
    // DOCUMENT TYPE
    // -------------------------------------------------

    document.getElementById("resultType").textContent =
        formatDocumentType(
            data.document_type ||
            data.extracted_data?.document_type ||
            "-"
        );


    // -------------------------------------------------
    // PROCESSING STATUS
    // -------------------------------------------------

    document.getElementById("resultStatus").textContent =
        data.processing_status ||
        data.status ||
        "Completed";


    // -------------------------------------------------
    // PROCESSING TIME
    // -------------------------------------------------

    if (data.processing_metadata) {

        const processingTime =
            data.processing_metadata.processing_time_ms;

        document.getElementById("processingTime").textContent =
            processingTime !== undefined &&
            processingTime !== null
                ? processingTime + " ms"
                : "-";

    } else {

        document.getElementById("processingTime").textContent =
            "-";
    }


    // -------------------------------------------------
    // EXTRACTED DATA
    // -------------------------------------------------

    document.getElementById("extractedData").textContent =
        JSON.stringify(
            data.extracted_data || {},
            null,
            2
        );


    // -------------------------------------------------
    // VALIDATION
    // -------------------------------------------------

    document.getElementById("validationData").textContent =
        JSON.stringify(
            data.validation || {},
            null,
            2
        );


    // -------------------------------------------------
    // RAW OCR TEXT
    // -------------------------------------------------

    document.getElementById("rawText").textContent =
        data.raw_text ||
        "No OCR text available.";


    // Scroll to result
    resultSection.scrollIntoView({
        behavior: "smooth"
    });
}


// =====================================================
// LOAD STORED DOCUMENTS
// =====================================================

async function loadDocuments() {

    const container =
        document.getElementById(
            "documentsContainer"
        );

    try {

        const response =
            await fetch(
                `${API_BASE}/documents`
            );

        if (!response.ok) {

            throw new Error(
                "Unable to load documents."
            );
        }

        const documents =
            await response.json();


        // No documents
        if (!documents.length) {

            container.innerHTML =
                "<p>No documents processed yet.</p>";

            return;
        }


        // -------------------------------------------------
        // CREATE TABLE
        // -------------------------------------------------

        let html = `
            <div class="table-wrapper">

                <table>

                    <thead>

                        <tr>

                            <th>Document Name</th>

                            <th>Type</th>

                            <th>Status</th>

                            <th>Processed At</th>

                            <th>Action</th>

                        </tr>

                    </thead>

                    <tbody>
        `;


        documents.forEach(doc => {

            html += `

                <tr>

                    <td>
                        ${escapeHtml(
                            doc.document_name || "-"
                        )}
                    </td>


                    <td>
                        ${formatDocumentType(
                            doc.document_type || "-"
                        )}
                    </td>


                    <td>

                        <span class="status-badge">

                            ${escapeHtml(
                                doc.processing_status ||
                                "completed"
                            )}

                        </span>

                    </td>


                    <td>
                        ${escapeHtml(
                            doc.processed_at || "-"
                        )}
                    </td>


                    <td>

                        <button
                            class="small-btn"
                            onclick="viewDocument(
                                '${encodeURIComponent(
                                    doc.document_name
                                )}'
                            )"
                        >
                            View
                        </button>

                    </td>

                </tr>

            `;

        });


        html += `

                    </tbody>

                </table>

            </div>

        `;


        container.innerHTML = html;


    } catch (error) {

        console.error(
            "Dashboard error:",
            error
        );

        container.innerHTML = `

            <p class="error">

                Unable to load documents:
                ${escapeHtml(error.message)}

            </p>

        `;
    }
}


// =====================================================
// VIEW STORED DOCUMENT
// =====================================================

async function viewDocument(encodedName) {

    const documentName =
        decodeURIComponent(encodedName);


    try {

        const response =
            await fetch(

                `${API_BASE}/documents/` +
                `${encodeURIComponent(documentName)}`

            );


        if (!response.ok) {

            const errorData =
                await response.json();

            throw new Error(

                errorData.detail?.error ||
                errorData.detail ||
                "Document not found."

            );
        }


        const data =
            await response.json();


        // Display stored document
        displayResult(data);


    } catch (error) {

        console.error(
            "View document error:",
            error
        );

        alert(
            "Unable to load document: " +
            error.message
        );
    }
}


// =====================================================
// FORMAT DOCUMENT TYPE
// =====================================================

function formatDocumentType(type) {

    if (!type || type === "-") {
        return "-";
    }

    return String(type)
        .replaceAll("_", " ")
        .replace(/\b\w/g, letter =>
            letter.toUpperCase()
        );
}


// =====================================================
// ESCAPE HTML
// =====================================================

function escapeHtml(value) {

    return String(value)

        .replaceAll("&", "&amp;")

        .replaceAll("<", "&lt;")

        .replaceAll(">", "&gt;")

        .replaceAll('"', "&quot;")

        .replaceAll("'", "&#039;");
}


// =====================================================
// INITIALIZE APPLICATION
// =====================================================

checkHealth();

loadDocuments();
