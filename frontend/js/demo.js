// ============================================================
// DataExtract - Document OCR Demo
// ============================================================

const API_URL = "http://127.0.0.1:8001/api/ocr";


// ============================================================
// DOM ELEMENTS
// ============================================================

const uploadBox = document.getElementById("uploadBox");
const fileInput = document.getElementById("fileInput");
const chooseFile = document.getElementById("chooseFile");
const fileName = document.getElementById("fileName");
const processBtn = document.getElementById("processBtn");
const loading = document.getElementById("loading");
const message = document.getElementById("message");
const results = document.getElementById("results");
const fieldsContainer = document.getElementById("fieldsContainer");
const ocrText = document.getElementById("ocrText");
const downloadBtn = document.getElementById("downloadBtn");


// ============================================================
// VARIABLES
// ============================================================

let selectedFile = null;
let lastResult = null;


// ============================================================
// CHOOSE FILE
// ============================================================

chooseFile.addEventListener("click", function (event) {

    event.preventDefault();

    fileInput.click();

});


// ============================================================
// FILE INPUT
// ============================================================

fileInput.addEventListener("change", function (event) {

    console.log("File input changed");

    const files = event.target.files;

    console.log("Files:", files);

    if (!files || files.length === 0) {

        console.log("No file selected");

        selectedFile = null;

        fileName.textContent = "No file selected";

        processBtn.disabled = true;

        return;
    }

    // Get first selected file
    selectedFile = files[0];

    console.log("Selected file:", selectedFile);
    console.log("File name:", selectedFile.name);
    console.log("File size:", selectedFile.size);
    console.log("File type:", selectedFile.type);


    // Display filename
    fileName.textContent =
        "Selected: " + selectedFile.name;


    // Enable process button
    processBtn.disabled = false;


    // Clear old message
    message.textContent = "";
    message.className = "";

});


// ============================================================
// DRAG OVER
// ============================================================

uploadBox.addEventListener("dragover", function (event) {

    event.preventDefault();

    uploadBox.classList.add("drag-over");

});


// ============================================================
// DRAG LEAVE
// ============================================================

uploadBox.addEventListener("dragleave", function () {

    uploadBox.classList.remove("drag-over");

});


// ============================================================
// DROP FILE
// ============================================================

uploadBox.addEventListener("drop", function (event) {

    event.preventDefault();

    uploadBox.classList.remove("drag-over");

    const files = event.dataTransfer.files;

    if (!files || files.length === 0) {

        return;
    }

    selectedFile = files[0];

    console.log(
        "Dropped file:",
        selectedFile.name
    );

    fileName.textContent =
        "Selected: " + selectedFile.name;

    processBtn.disabled = false;

});


// ============================================================
// PROCESS BUTTON
// ============================================================

processBtn.addEventListener("click", function () {

    console.log("Process button clicked");

    console.log(
        "Current selected file:",
        selectedFile
    );

    processDocument();

});


// ============================================================
// PROCESS DOCUMENT
// ============================================================

async function processDocument() {

    // --------------------------------------------------------
    // CHECK FILE
    // --------------------------------------------------------

    if (!selectedFile) {

        showMessage(
            "Please select a file first.",
            "error"
        );

        return;
    }


    console.log(
        "Starting OCR for:",
        selectedFile.name
    );


    // --------------------------------------------------------
    // CREATE FORMDATA
    // --------------------------------------------------------

    const formData = new FormData();


    // IMPORTANT:
    // FastAPI expects the field name "file"

    formData.append(
        "file",
        selectedFile,
        selectedFile.name
    );


    console.log(
        "FormData created successfully"
    );


    // --------------------------------------------------------
    // SHOW LOADING
    // --------------------------------------------------------

    processBtn.disabled = true;

    loading.style.display = "block";

    results.style.display = "none";

    message.textContent = "";


    try {

        console.log(
            "Sending request to:",
            API_URL
        );


        // ----------------------------------------------------
        // SEND TO BACKEND
        // ----------------------------------------------------

        const response = await fetch(
            API_URL,
            {
                method: "POST",
                body: formData
            }
        );


        console.log(
            "Response status:",
            response.status
        );


        // ----------------------------------------------------
        // GET RESPONSE
        // ----------------------------------------------------

        const data =
            await response.json();


        console.log(
            "Backend response:",
            data
        );


        // ----------------------------------------------------
        // CHECK BACKEND ERROR
        // ----------------------------------------------------

        if (!response.ok) {

            throw new Error(
                data.detail ||
                data.message ||
                "Document processing failed."
            );

        }


        // ----------------------------------------------------
        // SAVE RESULT
        // ----------------------------------------------------

        lastResult = data;


        // ----------------------------------------------------
        // OCR TEXT
        // ----------------------------------------------------

        const text =
            data.text ||
            data.ocr_text ||
            data.extracted_text ||
            "";


        ocrText.value = text;


        // ----------------------------------------------------
        // STRUCTURED FIELDS
        // ----------------------------------------------------

        displayFields(
            data.fields || {}
        );


        // ----------------------------------------------------
        // SHOW RESULTS
        // ----------------------------------------------------

        results.style.display = "block";


        showMessage(
            "Document processed successfully.",
            "success"
        );


        // ----------------------------------------------------
        // SCROLL
        // ----------------------------------------------------

        setTimeout(function () {

            results.scrollIntoView({
                behavior: "smooth"
            });

        }, 200);

    }

    catch (error) {

        console.error(
            "OCR ERROR:",
            error
        );


        showMessage(
            "Backend connection failed: " +
            error.message,
            "error"
        );

    }

    finally {

        loading.style.display = "none";

        processBtn.disabled = false;

    }

}


// ============================================================
// DISPLAY FIELDS
// ============================================================

function displayFields(fields) {

    fieldsContainer.innerHTML = "";


    const keys =
        Object.keys(fields);


    if (keys.length === 0) {

        fieldsContainer.innerHTML =
            "<p>No structured fields detected.</p>";

        return;
    }


    keys.forEach(function (key) {

        const field =
            document.createElement("div");

        field.className = "field";


        const label =
            document.createElement("label");

        label.textContent =
            formatLabel(key);


        const input =
            document.createElement("input");

        input.type = "text";

        input.value =
            fields[key] || "Not detected";

        input.readOnly = true;


        field.appendChild(label);

        field.appendChild(input);


        fieldsContainer.appendChild(field);

    });

}


// ============================================================
// FORMAT LABEL
// ============================================================

function formatLabel(text) {

    return text
        .replace(/_/g, " ")
        .replace(/\b\w/g, function (letter) {
            return letter.toUpperCase();
        });

}


// ============================================================
// MESSAGE
// ============================================================

function showMessage(text, type) {

    message.textContent = text;

    message.className = type;

    console.log(
        type.toUpperCase() + ":",
        text
    );

}


// ============================================================
// DOWNLOAD RESULT
// ============================================================

downloadBtn.addEventListener("click", function () {

    if (!lastResult) {

        showMessage(
            "No result available to download.",
            "error"
        );

        return;
    }


    const jsonData =
        JSON.stringify(
            lastResult,
            null,
            4
        );


    const blob =
        new Blob(
            [jsonData],
            {
                type: "application/json"
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

});


// ============================================================
// STARTUP
// ============================================================

console.log(
    "DataExtract frontend loaded."
);

console.log(
    "OCR API:",
    API_URL
);