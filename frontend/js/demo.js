// ============================================================
// DataExtract - OCR Demo Frontend
// ============================================================

// ============================================================
// CONFIGURATION
// ============================================================

const API_URL = "https://document-ocr-zthu.onrender.com/api/ocr";


// ============================================================
// DOM ELEMENTS
// ============================================================

const uploadBox = document.getElementById("uploadBox");
const fileInput = document.getElementById("fileInput");
const fileName = document.getElementById("fileName");
const processBtn = document.getElementById("processBtn");

const loading = document.getElementById("loading");
const message = document.getElementById("message");
const results = document.getElementById("results");

const fieldsContainer =
    document.getElementById("fieldsContainer");

const validationContainer =
    document.getElementById("validationContainer");

const matchingContainer =
    document.getElementById("matchingContainer");

const ocrText =
    document.getElementById("ocrText");

const downloadBtn =
    document.getElementById("downloadBtn");

const referenceText =
    document.getElementById("referenceText");

const calculateAccuracyBtn =
    document.getElementById("calculateAccuracyBtn");

const accuracyResult =
    document.getElementById("accuracyResult");

const characterAccuracy =
    document.getElementById("characterAccuracy");

const wordAccuracy =
    document.getElementById("wordAccuracy");

const correctWords =
    document.getElementById("correctWords");

const overallAccuracy =
    document.getElementById("overallAccuracy");


// ============================================================
// VARIABLES
// ============================================================

let selectedFile = null;
let latestResult = null;
let latestOCRText = "";


// ============================================================
// STARTUP
// ============================================================

console.log("====================================");
console.log("DataExtract frontend loaded");
console.log("OCR API:", API_URL);
console.log("====================================");


// ============================================================
// FILE SELECTION
// ============================================================

if (fileInput) {

    fileInput.addEventListener("change", function (event) {

        console.log("File input changed");

        const file = event.target.files[0];

        if (!file) {
            clearSelectedFile();
            return;
        }

        processSelectedFile(file);

    });

}


// ============================================================
// PROCESS SELECTED FILE
// ============================================================

function processSelectedFile(file) {

    console.log("Selected file:", file.name);
    console.log("File size:", file.size);
    console.log("File type:", file.type);

    const maxSize = 20 * 1024 * 1024;

    if (file.size === 0) {

        showError("The selected file is empty.");
        clearSelectedFile();
        return;

    }

    if (file.size > maxSize) {

        showError("File is larger than 20 MB.");
        clearSelectedFile();
        return;

    }

    const extension =
        file.name
            .split(".")
            .pop()
            .toLowerCase();

    const allowedExtensions = [
        "pdf",
        "jpg",
        "jpeg",
        "png",
        "tif",
        "tiff",
        "bmp"
    ];

    if (!allowedExtensions.includes(extension)) {

        showError(
            "Unsupported file type. Please select PDF, JPG, JPEG, PNG, TIFF or BMP."
        );

        clearSelectedFile();
        return;

    }

    selectedFile = file;

    if (fileName) {

        fileName.textContent =
            "✓ Selected: " + file.name;

        fileName.style.color = "#159447";

    }

    if (processBtn) {

        processBtn.disabled = false;

    }

    clearMessage();

    console.log("File successfully accepted.");

}


// ============================================================
// CLEAR FILE
// ============================================================

function clearSelectedFile() {

    selectedFile = null;

    if (fileInput) {
        fileInput.value = "";
    }

    if (fileName) {

        fileName.textContent =
            "No file selected";

        fileName.style.color =
            "#687d76";

    }

    if (processBtn) {

        processBtn.disabled = true;

    }

}


// ============================================================
// DRAG & DROP
// ============================================================

if (uploadBox) {

    uploadBox.addEventListener("dragover", function (event) {

        event.preventDefault();

        uploadBox.classList.add("dragging");

    });


    uploadBox.addEventListener("dragleave", function () {

        uploadBox.classList.remove("dragging");

    });


    uploadBox.addEventListener("drop", function (event) {

        event.preventDefault();

        uploadBox.classList.remove("dragging");

        const file =
            event.dataTransfer.files[0];

        if (file) {

            processSelectedFile(file);

        }

    });

}


// ============================================================
// PROCESS BUTTON
// ============================================================

if (processBtn) {

    processBtn.addEventListener("click", function (event) {

        event.preventDefault();

        console.log("====================================");
        console.log("PROCESS BUTTON CLICKED");
        console.log("====================================");

        if (!selectedFile) {

            showError(
                "Please select a file first."
            );

            return;

        }

        sendToBackend();

    });

}


// ============================================================
// SEND TO BACKEND
// ============================================================

async function sendToBackend() {

    clearMessage();

    if (!selectedFile) {

        showError("Please select a file first.");
        return;

    }

    if (loading) {

        loading.style.display = "block";

    }

    if (processBtn) {

        processBtn.disabled = true;
        processBtn.textContent = "Processing...";

    }

    if (results) {

        results.style.display = "none";

    }

    showProgress(
        10,
        "Uploading document..."
    );


    try {

        console.log("====================================");
        console.log("SENDING FILE TO BACKEND");
        console.log("====================================");

        console.log("API URL:", API_URL);
        console.log("File:", selectedFile.name);


        // ----------------------------------------------------
        // CREATE FORM DATA
        // ----------------------------------------------------

        const formData = new FormData();

        formData.append(
            "file",
            selectedFile
        );


        console.log("FormData created.");


        showProgress(
            20,
            "Uploading document..."
        );


        // ----------------------------------------------------
        // SEND REQUEST
        // ----------------------------------------------------

        console.log("Calling fetch...");


        const response = await fetch(
            API_URL,
            {
                method: "POST",
                body: formData
            }
        );


        console.log("Response received.");
        console.log(
            "HTTP Status:",
            response.status
        );


        showProgress(
            60,
            "Receiving OCR result..."
        );


        // ----------------------------------------------------
        // READ RESPONSE AS TEXT
        // ----------------------------------------------------

        const responseText =
            await response.text();


        console.log("====================================");
        console.log("RAW BACKEND RESPONSE");
        console.log("====================================");

        console.log(responseText);


        // ----------------------------------------------------
        // CHECK HTTP STATUS
        // ----------------------------------------------------

        if (!response.ok) {

            throw new Error(
                "Backend returned HTTP " +
                response.status +
                ": " +
                responseText
            );

        }


        // ----------------------------------------------------
        // PARSE JSON
        // ----------------------------------------------------

        let data;

        try {

            data =
                JSON.parse(responseText);

        }
        catch (jsonError) {

            console.error(
                "JSON parsing failed:",
                jsonError
            );

            console.error(
                "Backend response:",
                responseText
            );

            throw new Error(
                "Backend returned an invalid JSON response."
            );

        }


        console.log("====================================");
        console.log("PARSED OCR RESPONSE");
        console.log("====================================");

        console.log(data);


        // ----------------------------------------------------
        // SAVE RESULT
        // ----------------------------------------------------

        latestResult = data;


        showProgress(
            75,
            "Extracting fields..."
        );


        // ----------------------------------------------------
        // DISPLAY RESULT
        // ----------------------------------------------------

        showResults(data);


        showProgress(
            90,
            "Finalizing results..."
        );


        await new Promise(function (resolve) {

            setTimeout(resolve, 300);

        });


        showProgress(
            100,
            "Processing completed"
        );


        showSuccess(
            "Document processed successfully."
        );


        console.log(
            "OCR processing completed successfully."
        );


    }
    catch (error) {

        console.error("====================================");
        console.error("OCR ERROR");
        console.error("====================================");

        console.error(error);


        showError(
            "OCR processing failed: " +
            error.message
        );

    }
    finally {

        if (loading) {

            loading.style.display =
                "none";

        }

        if (processBtn) {

            processBtn.disabled =
                selectedFile === null;

            processBtn.textContent =
                "Process Document";

        }

    }

}


// ============================================================
// PROGRESS BAR
// ============================================================

function showProgress(percent, text) {

    let container =
        document.getElementById(
            "ocrProgressContainer"
        );

    if (!container) {

        container =
            document.createElement("div");

        container.id =
            "ocrProgressContainer";

        container.style.width =
            "100%";

        container.style.margin =
            "20px 0";

        container.innerHTML = `

            <div style="
                width:100%;
                height:10px;
                background:#e5e7eb;
                border-radius:10px;
                overflow:hidden;
            ">

                <div id="ocrProgressBar" style="
                    width:0%;
                    height:100%;
                    background:#159447;
                    border-radius:10px;
                    transition:width 0.4s ease;
                "></div>

            </div>

            <div id="ocrProgressText" style="
                margin-top:8px;
                text-align:center;
                font-size:14px;
                color:#687d76;
            "></div>
        `;

        if (processBtn && processBtn.parentNode) {

            processBtn.parentNode.insertBefore(
                container,
                processBtn.nextSibling
            );

        }

    }


    container.style.display =
        "block";


    const bar =
        document.getElementById(
            "ocrProgressBar"
        );

    const progressText =
        document.getElementById(
            "ocrProgressText"
        );


    if (bar) {

        bar.style.width =
            percent + "%";

    }


    if (progressText) {

        progressText.textContent =
            text + " " + percent + "%";

    }

}


// ============================================================
// SHOW RESULTS
// ============================================================

function showResults(data) {

    console.log("====================================");
    console.log("DISPLAYING RESULTS");
    console.log("====================================");

    console.log(data);


    if (results) {

        results.style.display =
            "block";

    }


    // ========================================================
    // OCR TEXT
    // ========================================================

    let text =
        data.full_text ||
        data.text ||
        data.ocr_text ||
        data.extracted_text ||
        "";


    if (
        !text &&
        data.result
    ) {

        text =
            data.result.full_text ||
            data.result.text ||
            data.result.ocr_text ||
            data.result.extracted_text ||
            "";

    }


    latestOCRText =
        String(text || "");


    if (ocrText) {

        ocrText.value =
            latestOCRText ||
            "No text detected.";

    }


    // ========================================================
    // FIELDS
    // ========================================================

    let fields =
        data.fields ||
        data.extracted_fields ||
        {};


    if (
        Object.keys(fields).length === 0 &&
        data.result
    ) {

        fields =
            data.result.fields ||
            data.result.extracted_fields ||
            {};

    }


    // If backend returns document_type,
    // company, name, date, amount directly

    if (
        Object.keys(fields).length === 0
    ) {

        const possibleFields = {};

        const fieldNames = [
            "document_type",
            "company",
            "name",
            "date",
            "amount",
            "email",
            "vehicle",
            "customer",
            "lr",
            "delivery",
            "origin",
            "destination",
            "gateOut",
            "gate_out",
            "weight",
            "weightKg",
            "invoice",
            "ewayBill",
            "eway_bill"
        ];


        fieldNames.forEach(function (key) {

            if (
                Object.prototype.hasOwnProperty.call(
                    data,
                    key
                )
            ) {

                possibleFields[key] =
                    data[key];

            }

        });


        fields =
            possibleFields;

    }


    displayFields(fields);


    // ========================================================
    // VALIDATION
    // ========================================================

    let validation =
        data.validation ||
        data.validations ||
        {};


    if (
        Object.keys(validation).length === 0 &&
        data.result
    ) {

        validation =
            data.result.validation ||
            data.result.validations ||
            {};

    }


    displayValidation(
        validation,
        fields
    );


    // ========================================================
    // MATCHING
    // ========================================================

    let matching =
        data.matching ||
        data.match ||
        {};


    if (
        Object.keys(matching).length === 0 &&
        data.result
    ) {

        matching =
            data.result.matching ||
            data.result.match ||
            {};

    }


    displayMatching(
        matching
    );


    // ========================================================
    // SCROLL TO RESULT
    // ========================================================

    setTimeout(function () {

        if (results) {

            results.scrollIntoView({
                behavior: "smooth"
            });

        }

    }, 200);

}


// ============================================================
// DISPLAY FIELDS
// ============================================================

function displayFields(fields) {

    if (!fieldsContainer) {
        return;
    }


    fieldsContainer.innerHTML = "";


    if (
        !fields ||
        Object.keys(fields).length === 0
    ) {

        fieldsContainer.innerHTML =
            "<p>No structured fields detected.</p>";

        return;

    }


    const grid =
        document.createElement("div");

    grid.className =
        "extracted-fields-grid";


    Object.entries(fields).forEach(
        function ([key, value]) {

            addExtractedField(
                grid,
                key,
                value
            );

        }
    );


    fieldsContainer.appendChild(
        grid
    );

}


// ============================================================
// ADD FIELD
// ============================================================

function addExtractedField(
    grid,
    key,
    value
) {

    const div =
        document.createElement("div");

    div.className =
        "extracted-field";


    const label =
        document.createElement("div");

    label.className =
        "field-label";

    label.textContent =
        formatLabel(key);


    const fieldValue =
        document.createElement("div");

    fieldValue.className =
        "field-value";


    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {

        fieldValue.textContent =
            "Not detected";

    }
    else if (
        typeof value === "object"
    ) {

        fieldValue.textContent =
            JSON.stringify(value);

    }
    else {

        fieldValue.textContent =
            String(value);

    }


    div.appendChild(label);
    div.appendChild(fieldValue);

    grid.appendChild(div);

}


// ============================================================
// VALIDATION
// ============================================================

function displayValidation(
    validation,
    fields
) {

    if (!validationContainer) {
        return;
    }


    validationContainer.innerHTML = "";


    const title =
        document.createElement("h3");

    title.textContent =
        "Validation";


    validationContainer.appendChild(
        title
    );


    if (
        validation &&
        Object.keys(validation).length > 0
    ) {

        Object.entries(validation).forEach(
            function ([key, value]) {

                let status = "PASS";
                let detail = "";


                if (
                    typeof value === "object" &&
                    value !== null
                ) {

                    status =
                        value.status ||
                        value.result ||
                        "PASS";

                    detail =
                        value.message ||
                        value.reason ||
                        value.description ||
                        "";

                }
                else {

                    const raw =
                        String(value);


                    if (/FAIL/i.test(raw)) {

                        status = "FAIL";

                        detail =
                            raw.replace(
                                /^FAIL\s*[—-]?\s*/i,
                                ""
                            );

                    }
                    else {

                        status = "PASS";

                        detail =
                            raw.replace(
                                /^PASS\s*[—-]?\s*/i,
                                ""
                            );

                    }

                }


                const row =
                    document.createElement("div");

                row.className =
                    "validation-row";


                const statusClass =
                    String(status).toLowerCase() ===
                    "fail"
                        ? "fail"
                        : "pass";


                row.innerHTML =
                    '<span class="validation-key">' +
                    escapeHtml(key) +
                    ':</span> ' +

                    '<span class="validation-status ' +
                    statusClass +
                    '">' +

                    escapeHtml(
                        String(status).toUpperCase()
                    ) +

                    '</span> — ' +

                    escapeHtml(
                        detail
                    );


                validationContainer.appendChild(
                    row
                );

            }
        );


        return;

    }


    if (
        !fields ||
        Object.keys(fields).length === 0
    ) {

        validationContainer.innerHTML +=
            '<div class="validation-row">' +
            'No validation data returned by the backend.' +
            '</div>';

        return;

    }


    Object.entries(fields).forEach(
        function ([key, value]) {

            const valid =
                value !== null &&
                value !== undefined &&
                String(value).trim() !== "";


            const row =
                document.createElement("div");

            row.className =
                "validation-row";


            row.innerHTML =
                '<span class="validation-key">' +
                escapeHtml(key) +
                ':</span> ' +

                '<span class="validation-status ' +
                (valid ? "pass" : "fail") +
                '">' +

                (valid ? "PASS" : "FAIL") +

                '</span> — ' +

                escapeHtml(
                    valid
                        ? formatLabel(key) +
                          " extracted"
                        : formatLabel(key) +
                          " not detected"
                );


            validationContainer.appendChild(
                row
            );

        }
    );

}


// ============================================================
// MATCHING
// ============================================================

function displayMatching(matching) {

    if (!matchingContainer) {
        return;
    }


    matchingContainer.innerHTML = "";


    const title =
        document.createElement("h3");

    title.textContent =
        "Matching";


    matchingContainer.appendChild(
        title
    );


    if (
        !matching ||
        Object.keys(matching).length === 0
    ) {

        matchingContainer.innerHTML +=
            '<div class="validation-row">' +
            'No matching data returned by the backend.' +
            '</div>';

        return;

    }


    const grid =
        document.createElement("div");

    grid.className =
        "matching-grid";


    const driverSource =
        matching.driverSource ||
        matching.driver_source ||
        matching.driver ||
        "";


    const distance =
        matching.distance ??
        matching.distanceKm ??
        matching.distance_km ??
        "";


    const distanceSource =
        matching.distanceSource ||
        matching.distance_source ||
        "";


    const trip =
        matching.trip ||
        matching.tripId ||
        matching.trip_id ||
        "";


    addMatchingField(
        grid,
        "DRIVER SOURCE",
        driverSource
    );


    addMatchingField(
        grid,
        "DISTANCE (KM)",
        distance
    );


    addMatchingField(
        grid,
        "DISTANCE SOURCE",
        distanceSource
    );


    addMatchingField(
        grid,
        "TRIP",
        trip
    );


    matchingContainer.appendChild(
        grid
    );

}


// ============================================================
// MATCHING FIELD
// ============================================================

function addMatchingField(
    grid,
    labelText,
    value
) {

    const div =
        document.createElement("div");

    div.className =
        "extracted-field";


    const label =
        document.createElement("div");

    label.className =
        "matching-label";

    label.textContent =
        labelText;


    const fieldValue =
        document.createElement("div");

    fieldValue.className =
        "matching-value";


    fieldValue.textContent =
        value === null ||
        value === undefined ||
        value === ""
            ? "-"
            : String(value);


    div.appendChild(label);
    div.appendChild(fieldValue);


    grid.appendChild(div);

}


// ============================================================
// ACCURACY
// ============================================================

if (calculateAccuracyBtn) {

    calculateAccuracyBtn.addEventListener(
        "click",
        function (event) {

            event.preventDefault();

            calculateOCRAccuracy();

        }
    );

}


function calculateOCRAccuracy() {

    const reference =
        referenceText
            ? referenceText.value.trim()
            : "";


    if (!reference) {

        showError(
            "Please enter the correct text from the original document."
        );

        return;

    }


    const ocr =
        String(
            latestOCRText || ""
        ).trim();


    if (!ocr) {

        showError(
            "No OCR text is available."
        );

        return;

    }


    const characterSimilarity =
        calculateSimilarity(
            reference,
            ocr
        );


    const referenceWords =
        normalizeWords(reference);


    const ocrWords =
        normalizeWords(ocr);


    const wordResult =
        calculateWordAccuracy(
            referenceWords,
            ocrWords
        );


    const overall =
        (
            characterSimilarity +
            wordResult.accuracy
        ) / 2;


    if (characterAccuracy) {

        characterAccuracy.textContent =
            formatPercentage(
                characterSimilarity
            );

    }


    if (wordAccuracy) {

        wordAccuracy.textContent =
            formatPercentage(
                wordResult.accuracy
            );

    }


    if (correctWords) {

        correctWords.textContent =
            wordResult.correct +
            " / " +
            wordResult.total;

    }


    if (overallAccuracy) {

        overallAccuracy.textContent =
            formatPercentage(
                overall
            );

    }


    if (accuracyResult) {

        accuracyResult.style.display =
            "block";

    }

}


// ============================================================
// TEXT NORMALIZATION
// ============================================================

function normalizeText(text) {

    return String(text)
        .replace(/\r\n/g, "\n")
        .replace(/\r/g, "\n")
        .replace(/\s+/g, " ")
        .trim()
        .toLowerCase();

}


function normalizeWords(text) {

    const normalized =
        normalizeText(text);


    if (!normalized) {
        return [];
    }


    return normalized
        .split(" ")
        .filter(Boolean);

}


// ============================================================
// SIMILARITY
// ============================================================

function calculateSimilarity(
    reference,
    actual
) {

    const a =
        normalizeText(reference);

    const b =
        normalizeText(actual);


    if (a === b) {
        return 100;
    }


    if (!a.length) {
        return 0;
    }


    const distance =
        levenshteinDistance(
            a,
            b
        );


    const maxLength =
        Math.max(
            a.length,
            b.length
        );


    return Math.max(
        0,
        (
            1 -
            distance / maxLength
        ) * 100
    );

}


// ============================================================
// LEVENSHTEIN
// ============================================================

function levenshteinDistance(a, b) {

    const matrix =
        Array.from(
            {
                length: a.length + 1
            },
            () =>
                new Array(
                    b.length + 1
                )
        );


    for (
        let i = 0;
        i <= a.length;
        i++
    ) {

        matrix[i][0] = i;

    }


    for (
        let j = 0;
        j <= b.length;
        j++
    ) {

        matrix[0][j] = j;

    }


    for (
        let i = 1;
        i <= a.length;
        i++
    ) {

        for (
            let j = 1;
            j <= b.length;
            j++
        ) {

            const cost =
                a[i - 1] ===
                b[j - 1]
                    ? 0
                    : 1;


            matrix[i][j] =
                Math.min(

                    matrix[i - 1][j] + 1,

                    matrix[i][j - 1] + 1,

                    matrix[i - 1][j - 1] +
                    cost

                );

        }

    }


    return matrix[a.length][b.length];

}


// ============================================================
// WORD ACCURACY
// ============================================================

function calculateWordAccuracy(
    referenceWords,
    ocrWords
) {

    if (
        referenceWords.length === 0
    ) {

        return {
            accuracy: 0,
            correct: 0,
            total: 0
        };

    }


    let correct = 0;


    const minLength =
        Math.min(
            referenceWords.length,
            ocrWords.length
        );


    for (
        let i = 0;
        i < minLength;
        i++
    ) {

        if (
            referenceWords[i] ===
            ocrWords[i]
        ) {

            correct++;

        }

    }


    const accuracy =
        (
            correct /
            referenceWords.length
        ) * 100;


    return {

        accuracy:
            Math.max(
                0,
                Math.min(
                    100,
                    accuracy
                )
            ),

        correct:
            correct,

        total:
            referenceWords.length

    };

}


// ============================================================
// FORMAT
// ============================================================

function formatPercentage(value) {

    return (
        Math.max(
            0,
            Math.min(
                100,
                value
            )
        )
        .toFixed(2) +
        "%"
    );

}


function formatLabel(key) {

    return String(key)

        .replace(
            /([a-z])([A-Z])/g,
            "$1 $2"
        )

        .replace(
            /_/g,
            " "
        )

        .replace(
            /\b\w/g,
            function (letter) {
                return letter.toUpperCase();
            }
        );

}


// ============================================================
// ESCAPE HTML
// ============================================================

function escapeHtml(value) {

    return String(value)

        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");

}


// ============================================================
// MESSAGES
// ============================================================

function showError(text) {

    if (!message) {
        return;
    }


    message.innerHTML =
        '<div class="error">' +
        escapeHtml(text) +
        '</div>';

}


function showSuccess(text) {

    if (!message) {
        return;
    }


    message.innerHTML =
        '<div class="success">' +
        escapeHtml(text) +
        '</div>';

}


function clearMessage() {

    if (message) {

        message.innerHTML = "";

    }

}


// ============================================================
// DOWNLOAD RESULT
// ============================================================

if (downloadBtn) {

    downloadBtn.addEventListener(
        "click",
        function (event) {

            event.preventDefault();


            if (!latestResult) {

                showError(
                    "No result available to download."
                );

                return;

            }


            const downloadData = {

                ...latestResult,

                ocr_accuracy: {

                    character_accuracy:
                        characterAccuracy
                            ? characterAccuracy.textContent
                            : "Not calculated",

                    word_accuracy:
                        wordAccuracy
                            ? wordAccuracy.textContent
                            : "Not calculated",

                    correct_words:
                        correctWords
                            ? correctWords.textContent
                            : "Not calculated",

                    overall_accuracy:
                        overallAccuracy
                            ? overallAccuracy.textContent
                            : "Not calculated"

                }

            };


            const blob =
                new Blob(
                    [
                        JSON.stringify(
                            downloadData,
                            null,
                            4
                        )
                    ],
                    {
                        type:
                            "application/json"
                    }
                );


            const url =
                URL.createObjectURL(blob);


            const link =
                document.createElement("a");


            link.href = url;

            link.download =
                "dataextract-result.json";


            document.body.appendChild(link);

            link.click();

            document.body.removeChild(link);

            URL.revokeObjectURL(url);

        }
    );

}


// ============================================================
// PREVENT ACCIDENTAL FORM SUBMISSION
// ============================================================

document.addEventListener(
    "submit",
    function (event) {

        event.preventDefault();

    }
);


console.log(
    "DataExtract frontend ready."
);