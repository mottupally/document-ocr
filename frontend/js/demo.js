// ============================================================
// DataExtract - Document OCR Demo
// Clean Frontend JavaScript
// ============================================================


// ============================================================
// CONFIGURATION
// ============================================================

// LOCAL BACKEND
const API_URL = "https://document-ocr-zthu.onrender.com/api/ocr";

// WHEN DEPLOYING TO RENDER, CHANGE TO:
// const API_URL = "https://YOUR-BACKEND.onrender.com/api/ocr";


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


// Accuracy elements
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
// PROGRESS BAR
// ============================================================

let progressTimer = null;

function showProgress(percent, messageText) {

    let progressContainer =
        document.getElementById("ocrProgressContainer");

    // Create progress bar if it doesn't already exist
    if (!progressContainer) {

        progressContainer =
            document.createElement("div");

        progressContainer.id =
            "ocrProgressContainer";

        progressContainer.style.width = "100%";
        progressContainer.style.marginTop = "20px";
        progressContainer.style.display = "none";

        progressContainer.innerHTML = `
            <div style="
                width: 100%;
                height: 10px;
                background: #e5e7eb;
                border-radius: 10px;
                overflow: hidden;
            ">
                <div id="ocrProgressBar" style="
                    width: 0%;
                    height: 100%;
                    background: #159447;
                    border-radius: 10px;
                    transition: width 0.5s ease;
                "></div>
            </div>

            <div id="ocrProgressText" style="
                margin-top: 8px;
                text-align: center;
                font-size: 14px;
                color: #687d76;
            ">
                Preparing...
            </div>
        `;

        if (processBtn && processBtn.parentNode) {
            processBtn.parentNode.appendChild(
                progressContainer
            );
        }
    }

    const progressBar =
        document.getElementById("ocrProgressBar");

    const progressText =
        document.getElementById("ocrProgressText");

    progressContainer.style.display = "block";

    if (progressBar) {
        progressBar.style.width =
            Math.min(100, Math.max(0, percent)) + "%";
    }

    if (progressText) {
        progressText.textContent =
            messageText + " " + percent + "%";
    }
}


// ============================================================
// HIDE PROGRESS BAR
// ============================================================

function hideProgress() {

    if (progressTimer) {
        clearTimeout(progressTimer);
        progressTimer = null;
    }

    const progressContainer =
        document.getElementById(
            "ocrProgressContainer"
        );

    if (progressContainer) {
        progressContainer.style.display = "none";
    }
}


// ============================================================
// START ESTIMATED PROGRESS
// ============================================================

function startEstimatedProgress() {

    showProgress(
        10,
        "Uploading document..."
    );

    setTimeout(function () {

        showProgress(
            25,
            "Preparing document..."
        );

    }, 500);

    setTimeout(function () {

        showProgress(
            40,
            "Running OCR..."
        );

    }, 1500);

    setTimeout(function () {

        showProgress(
            55,
            "Processing OCR text..."
        );

    }, 4000);

    setTimeout(function () {

        showProgress(
            65,
            "Extracting fields..."
        );

    }, 7000);

    setTimeout(function () {

        showProgress(
            75,
            "Classifying document..."
        );

    }, 10000);

    setTimeout(function () {

        showProgress(
            85,
            "Validating extracted data..."
        );

    }, 13000);

    setTimeout(function () {

        showProgress(
            90,
            "Finalizing results..."
        );

    }, 16000);
}

// ============================================================
// STARTUP
// ============================================================

console.log("====================================");
console.log("DataExtract frontend loaded");
console.log("OCR API:", API_URL);
console.log("====================================");


// ============================================================
// FILE INPUT
// ============================================================

if (fileInput) {

    fileInput.addEventListener(
        "change",
        function (event) {

            console.log("File input changed.");

            const files = event.target.files;

            if (!files || files.length === 0) {

                clearSelectedFile();

                return;
            }

            processSelectedFile(files[0]);

        }
    );

}


// ============================================================
// PROCESS SELECTED FILE
// ============================================================

function processSelectedFile(file) {

    console.log("Selected file:", file.name);

    console.log("File size:", file.size);

    console.log("File type:", file.type);


    // --------------------------------------------------------
    // FILE SIZE
    // --------------------------------------------------------

    const maxSize =
        20 * 1024 * 1024;


    if (file.size === 0) {

        showError(
            "The selected file is empty."
        );

        clearSelectedFile();

        return;
    }


    if (file.size > maxSize) {

        showError(
            "File is larger than 20 MB."
        );

        clearSelectedFile();

        return;
    }


    // --------------------------------------------------------
    // FILE EXTENSION
    // --------------------------------------------------------

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


    if (
        !allowedExtensions.includes(extension)
    ) {

        showError(
            "Unsupported file type. Please select PDF, JPG, JPEG, PNG, TIFF or BMP."
        );

        clearSelectedFile();

        return;
    }


    // --------------------------------------------------------
    // SAVE FILE
    // --------------------------------------------------------

    selectedFile = file;


    // --------------------------------------------------------
    // DISPLAY FILE NAME
    // --------------------------------------------------------

    if (fileName) {

        fileName.textContent =
            "✓ Selected: " + file.name;

        fileName.style.color =
            "#159447";
    }


    // --------------------------------------------------------
    // ENABLE PROCESS BUTTON
    // --------------------------------------------------------

    if (processBtn) {

        processBtn.disabled = false;
    }


    clearMessage();


    console.log(
        "File successfully accepted."
    );

}


// ============================================================
// CLEAR SELECTED FILE
// ============================================================

function clearSelectedFile() {

    hideProgress();

    selectedFile = null;

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
// DRAG OVER
// ============================================================

if (uploadBox) {

    uploadBox.addEventListener(
        "dragover",
        function (event) {

            event.preventDefault();

            uploadBox.classList.add(
                "dragging"
            );

        }
    );

}


// ============================================================
// DRAG LEAVE
// ============================================================

if (uploadBox) {

    uploadBox.addEventListener(
        "dragleave",
        function () {

            uploadBox.classList.remove(
                "dragging"
            );

        }
    );

}


// ============================================================
// DROP
// ============================================================

if (uploadBox) {

    uploadBox.addEventListener(
        "drop",
        function (event) {

            event.preventDefault();

            uploadBox.classList.remove(
                "dragging"
            );


            const files =
                event.dataTransfer.files;


            if (!files || files.length === 0) {

                return;
            }


            processSelectedFile(
                files[0]
            );

        }
    );

}


// ============================================================
// PROCESS BUTTON
// ============================================================

if (processBtn) {

    processBtn.addEventListener(
        "click",
        function (event) {

            // IMPORTANT:
            // Prevent page refresh.
            event.preventDefault();


            console.log(
                "Process Document clicked."
            );


            console.log(
                "Current selected file:",
                selectedFile
            );


            if (!selectedFile) {

                showError(
                    "Please select a file first."
                );

                return;
            }


            sendToBackend();

        }
    );

}


// ============================================================
// SEND FILE TO BACKEND
// ============================================================

async function sendToBackend() {

    clearMessage();

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

    startEstimatedProgress();

    try {

        const formData = new FormData();

        formData.append(
            "file",
            selectedFile,
            selectedFile.name
        );

        showProgress(
            15,
            "Uploading document..."
        );

        await new Promise(
            resolve => setTimeout(resolve, 300)
        );

        showProgress(
            35,
            "Running OCR..."
        );

        const response = await fetch(
            API_URL,
            {
                method: "POST",
                body: formData
            }
        );

        showProgress(
            70,
            "Extracting fields..."
        );

        const responseText =
            await response.text();

        let data;

        try {
            data = JSON.parse(responseText);
        }
        catch (error) {
            throw new Error(
                "Backend did not return valid JSON."
            );
        }

        if (!response.ok) {
            throw new Error(
                data.detail ||
                data.message ||
                "Document processing failed."
            );
        }

        showProgress(
            85,
            "Validating extracted data..."
        );

        await new Promise(
            resolve => setTimeout(resolve, 300)
        );

        showProgress(
            95,
            "Finalizing results..."
        );

        latestResult = data;

        showProgress(
            100,
            "Processing completed"
        );

        showResults(data);

        showSuccess(
            "Document processed successfully."
        );

        progressTimer = setTimeout(
            hideProgress,
            3000
        );

    }
    catch (error) {

        console.error(
            "OCR ERROR:",
            error
        );

        showError(
            "Backend connection failed: " +
            error.message
        );

        progressTimer = setTimeout(
            hideProgress,
            3000
        );

    }
    finally {

        if (loading) {
            loading.style.display = "none";
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
// SHOW RESULTS
// ============================================================

function showResults(data) {

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


    // Some backends return result object
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
    // STRUCTURED FIELDS
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


    displayFields(
        fields
    );


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
    // RESET ACCURACY
    // ========================================================

    if (accuracyResult) {

        accuracyResult.style.display =
            "none";
    }


    if (characterAccuracy) {

        characterAccuracy.textContent =
            "0%";
    }


    if (wordAccuracy) {

        wordAccuracy.textContent =
            "0%";
    }


    if (correctWords) {

        correctWords.textContent =
            "0 / 0";
    }


    if (overallAccuracy) {

        overallAccuracy.textContent =
            "0%";
    }


    // ========================================================
    // SCROLL
    // ========================================================

    setTimeout(
        function () {

            if (results) {

                results.scrollIntoView({
                    behavior: "smooth"
                });

            }

        },
        200
    );

}


// ============================================================
// DISPLAY FIELDS
// ============================================================

function displayFields(fields) {

    if (!fieldsContainer) {

        return;
    }


    fieldsContainer.innerHTML =
        "";


    if (
        !fields ||
        Object.keys(fields).length === 0
    ) {

        const empty =
            document.createElement("p");

        empty.textContent =
            "No structured fields detected.";

        fieldsContainer.appendChild(
            empty
        );

        return;
    }


    const grid =
        document.createElement("div");

    grid.className =
        "extracted-fields-grid";


    // Preferred order
    const preferredOrder = [

        "vehicle",
        "customer",

        "lr",
        "delivery",

        "origin",
        "destination",

        "gateOut",
        "gate_out",
        "gateout",

        "weight",
        "weightKg",
        "weight_kg",

        "invoice",
        "ewayBill",
        "eway_bill",
        "eWayBill"

    ];


    const used =
        new Set();


    // --------------------------------------------------------
    // Preferred fields
    // --------------------------------------------------------

    preferredOrder.forEach(
        function (key) {

            if (
                Object.prototype.hasOwnProperty.call(
                    fields,
                    key
                )
            ) {

                addExtractedField(
                    grid,
                    key,
                    fields[key]
                );

                used.add(key);

            }

        }
    );


    // --------------------------------------------------------
    // Remaining fields
    // --------------------------------------------------------

    Object.entries(fields).forEach(
        function ([key, value]) {

            if (
                !used.has(key)
            ) {

                addExtractedField(
                    grid,
                    key,
                    value
                );

            }

        }
    );


    fieldsContainer.appendChild(
        grid
    );

}


// ============================================================
// ADD EXTRACTED FIELD
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
            JSON.stringify(
                value
            );

    }
    else {

        fieldValue.textContent =
            String(value);

    }


    div.appendChild(
        label
    );

    div.appendChild(
        fieldValue
    );

    grid.appendChild(
        div
    );

}


// ============================================================
// DISPLAY VALIDATION
// ============================================================

function displayValidation(
    validation,
    fields
) {

    if (!validationContainer) {

        return;
    }


    validationContainer.innerHTML =
        "";


    const title =
        document.createElement("h3");

    title.textContent =
        "Validation";

    validationContainer.appendChild(
        title
    );


    // --------------------------------------------------------
    // BACKEND VALIDATION EXISTS
    // --------------------------------------------------------

    if (
        validation &&
        Object.keys(validation).length > 0
    ) {

        Object.entries(validation).forEach(
            function ([key, value]) {

                let status =
                    "PASS";

                let detail =
                    "";


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


                    if (
                        /FAIL/i.test(raw)
                    ) {

                        status =
                            "FAIL";

                        detail =
                            raw.replace(
                                /^FAIL\s*[—-]?\s*/i,
                                ""
                            );

                    }
                    else {

                        status =
                            "PASS";

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


    // --------------------------------------------------------
    // FALLBACK VALIDATION
    // --------------------------------------------------------

    if (
        !fields ||
        Object.keys(fields).length === 0
    ) {

        const row =
            document.createElement("div");

        row.className =
            "validation-row";

        row.textContent =
            "No validation data returned by the backend.";

        validationContainer.appendChild(
            row
        );

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
// DISPLAY MATCHING
// ============================================================

function displayMatching(
    matching
) {

    if (!matchingContainer) {

        return;
    }


    matchingContainer.innerHTML =
        "";


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

        const note =
            document.createElement("div");

        note.className =
            "validation-row";

        note.textContent =
            "No matching data returned by the backend.";

        matchingContainer.appendChild(
            note
        );

        return;
    }


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


    const grid =
        document.createElement("div");

    grid.className =
        "matching-grid";


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
        trip,
        true
    );


    matchingContainer.appendChild(
        grid
    );

}


// ============================================================
// ADD MATCHING FIELD
// ============================================================

function addMatchingField(
    grid,
    labelText,
    value,
    isTrip = false
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


    if (
        isTrip &&
        value
    ) {

        fieldValue.classList.add(
            "trip-link"
        );

    }


    fieldValue.textContent =
        value === null ||
        value === undefined ||
        value === ""
            ? "-"
            : String(value);


    div.appendChild(
        label
    );

    div.appendChild(
        fieldValue
    );


    grid.appendChild(
        div
    );

}


// ============================================================
// OCR ACCURACY BUTTON
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


// ============================================================
// CALCULATE OCR ACCURACY
// ============================================================

function calculateOCRAccuracy() {

    // --------------------------------------------------------
    // CHECK REFERENCE TEXT
    // --------------------------------------------------------

    const reference =
        referenceText
            ? referenceText.value.trim()
            : "";


    if (!reference) {

        showError(
            "Please enter the correct text from the original document before calculating accuracy."
        );

        return;
    }


    // --------------------------------------------------------
    // CHECK OCR
    // --------------------------------------------------------

    const ocr =
        String(
            latestOCRText || ""
        ).trim();


    if (!ocr) {

        showError(
            "No OCR text is available. Please process a document first."
        );

        return;
    }


    console.log(
        "Reference text:",
        reference
    );


    console.log(
        "OCR text:",
        ocr
    );


    // ========================================================
    // CHARACTER ACCURACY
    // ========================================================

    const characterSimilarity =
        calculateSimilarity(
            reference,
            ocr
        );


    // ========================================================
    // WORD ACCURACY
    // ========================================================

    const referenceWords =
        normalizeWords(
            reference
        );


    const ocrWords =
        normalizeWords(
            ocr
        );


    const wordResult =
        calculateWordAccuracy(
            referenceWords,
            ocrWords
        );


    // ========================================================
    // OVERALL ACCURACY
    // ========================================================

    const overall =
        (
            characterSimilarity +
            wordResult.accuracy
        ) / 2;


    // ========================================================
    // DISPLAY
    // ========================================================

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


    console.log(
        "Character accuracy:",
        characterSimilarity
    );


    console.log(
        "Word accuracy:",
        wordResult.accuracy
    );


    console.log(
        "Overall accuracy:",
        overall
    );

}


// ============================================================
// NORMALIZE TEXT
// ============================================================

function normalizeText(text) {

    return String(text)

        .replace(
            /\r\n/g,
            "\n"
        )

        .replace(
            /\r/g,
            "\n"
        )

        .replace(
            /\s+/g,
            " "
        )

        .trim()
        .toLowerCase();

}


// ============================================================
// NORMALIZE WORDS
// ============================================================

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
// CHARACTER SIMILARITY
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


    if (maxLength === 0) {

        return 100;
    }


    return Math.max(
        0,
        (
            1 -
            distance / maxLength
        ) * 100
    );

}


// ============================================================
// LEVENSHTEIN DISTANCE
// ============================================================

function levenshteinDistance(
    a,
    b
) {

    const matrix =
        Array.from(
            {
                length: a.length + 1
            },
            function () {

                return new Array(
                    b.length + 1
                );

            }
        );


    for (
        let i = 0;
        i <= a.length;
        i++
    ) {

        matrix[i][0] =
            i;

    }


    for (
        let j = 0;
        j <= b.length;
        j++
    ) {

        matrix[0][j] =
            j;

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
                a[i - 1] === b[j - 1]
                    ? 0
                    : 1;


            matrix[i][j] =
                Math.min(

                    matrix[i - 1][j] + 1,

                    matrix[i][j - 1] + 1,

                    matrix[i - 1][j - 1] + cost

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


    const distance =
        levenshteinDistance(
            referenceWords.join("\u0001"),
            ocrWords.join("\u0001")
        );


    // --------------------------------------------------------
    // Count exact word positions
    // --------------------------------------------------------

    let correct =
        0;


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


    // --------------------------------------------------------
    // Word-level similarity
    // --------------------------------------------------------

    const maxWords =
        Math.max(
            referenceWords.length,
            ocrWords.length
        );


    let similarity =
        0;


    if (maxWords > 0) {

        similarity =
            (
                1 -
                distance /
                Math.max(
                    1,
                    maxWords
                )
            ) * 100;

    }


    // Exact position matches are more meaningful
    // for OCR comparison, so use the position score.
    const positionAccuracy =
        (
            correct /
            referenceWords.length
        ) * 100;


    // Use the better representation while keeping
    // the score bounded between 0 and 100.
    const accuracy =
        Math.max(
            0,
            Math.min(
                100,
                positionAccuracy
            )
        );


    return {

        accuracy: accuracy,

        correct: correct,

        total: referenceWords.length

    };

}


// ============================================================
// FORMAT PERCENTAGE
// ============================================================

function formatPercentage(
    value
) {

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


// ============================================================
// FORMAT LABEL
// ============================================================

function formatLabel(
    key
) {

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

function escapeHtml(
    value
) {

    return String(value)

        .replace(
            /&/g,
            "&amp;"
        )

        .replace(
            /</g,
            "&lt;"
        )

        .replace(
            />/g,
            "&gt;"
        )

        .replace(
            /"/g,
            "&quot;"
        )

        .replace(
            /'/g,
            "&#039;"
        );

}


// ============================================================
// ERROR MESSAGE
// ============================================================

function showError(
    text
) {

    if (!message) {

        return;
    }


    message.innerHTML =
        '<div class="error">' +
        escapeHtml(text) +
        '</div>';

}


// ============================================================
// SUCCESS MESSAGE
// ============================================================

function showSuccess(
    text
) {

    if (!message) {

        return;
    }


    message.innerHTML =
        '<div class="success">' +
        escapeHtml(text) +
        '</div>';

}


// ============================================================
// CLEAR MESSAGE
// ============================================================

function clearMessage() {

    if (message) {

        message.innerHTML =
            "";

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


            // Add accuracy information
            // if it has already been calculated.

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
                URL.createObjectURL(
                    blob
                );


            const link =
                document.createElement(
                    "a"
                );


            link.href =
                url;


            link.download =
                "dataextract-result.json";


            document.body.appendChild(
                link
            );


            link.click();


            document.body.removeChild(
                link
            );


            URL.revokeObjectURL(
                url
            );

        }
    );

}


// ============================================================
// PREVENT FORM REFRESH
// ============================================================

// This is an extra safety measure.
// Your current HTML does not use a form,
// but this prevents accidental refresh if
// one is added later.

document.addEventListener(
    "submit",
    function (event) {

        event.preventDefault();

    }
);


// ============================================================
// FINAL LOG
// ============================================================

console.log(
    "DataExtract frontend ready."
);