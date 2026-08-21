import os
import uuid
import shutil

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException
)

from fastapi.middleware.cors import CORSMiddleware

from ocr import process_document

from extractor import extract_fields


# --------------------------------------------------
# CREATE APP
# --------------------------------------------------

app = FastAPI(
    title="DataExtract OCR API",
    description="Multi-document OCR and field extraction API",
    version="1.0.0"
)


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)


# --------------------------------------------------
# UPLOAD DIRECTORY
# --------------------------------------------------

UPLOAD_DIR = "uploads"

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)


# --------------------------------------------------
# ALLOWED FILE TYPES
# --------------------------------------------------

ALLOWED_EXTENSIONS = {

    ".pdf",
    ".jpg",
    ".jpeg",
    ".png",
    ".tif",
    ".tiff",
    ".bmp"

}


# --------------------------------------------------
# ROOT
# --------------------------------------------------

@app.get("/")
def root():

    return {

        "message":
            "DataExtract OCR API is running",

        "docs":
            "/docs"

    }


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/health")
def health():

    return {

        "status": "healthy",

        "service":
            "DataExtract OCR"

    }


# --------------------------------------------------
# UPLOAD AND PROCESS DOCUMENT
# --------------------------------------------------

@app.post("/api/ocr")
async def process_uploaded_document(
    file: UploadFile = File(...)
):

    # Check filename

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No filename provided."
        )


    # Get extension

    extension = os.path.splitext(
        file.filename
    )[1].lower()


    # Validate extension

    if extension not in ALLOWED_EXTENSIONS:

        raise HTTPException(

            status_code=400,

            detail=(
                "Unsupported file type. "
                "Allowed: PDF, JPG, JPEG, "
                "PNG, TIFF, BMP"
            )

        )


    # Generate unique filename

    unique_filename = (
        f"{uuid.uuid4()}{extension}"
    )


    file_path = os.path.join(
        UPLOAD_DIR,
        unique_filename
    )


    try:

        # Save uploaded file

        with open(
            file_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )


        # OCR

        extracted_text = process_document(
            file_path
        )


        # Extract fields

        fields = extract_fields(
            extracted_text
        )


        # Return result

        return {

            "success": True,

            "filename":
                file.filename,

            "fields":
                fields,

            "full_text":
                extracted_text

        }


    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=f"OCR processing failed: {str(e)}"

        )


    finally:

        # Delete temporary uploaded file

        if os.path.exists(file_path):

            os.remove(file_path)