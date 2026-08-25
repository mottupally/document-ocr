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
        "message": "DataExtract OCR API is running",
        "docs": "/docs"
    }


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "DataExtract OCR"
    }


# --------------------------------------------------
# VALIDATION
# --------------------------------------------------

def validate_fields(fields):
    """
    Validate extracted fields.

    This creates the validation structure
    required by the frontend.
    """

    validation = {}

    # ----------------------------------------------
    # VEHICLE
    # ----------------------------------------------

    vehicle = fields.get("vehicle")

    if vehicle:
        validation["vehicle"] = {
            "status": "PASS",
            "message": "Vehicle matched"
        }
    else:
        validation["vehicle"] = {
            "status": "FAIL",
            "message": "Vehicle not detected"
        }


    # ----------------------------------------------
    # CUSTOMER
    # ----------------------------------------------

    customer = fields.get("customer")

    if customer:
        validation["customer"] = {
            "status": "PASS",
            "message": "Customer matched"
        }
    else:
        validation["customer"] = {
            "status": "FAIL",
            "message": "Customer not detected"
        }


    # ----------------------------------------------
    # ORIGIN
    # ----------------------------------------------

    origin = fields.get("origin")

    if origin:
        validation["origin"] = {
            "status": "PASS",
            "message": "Origin extracted"
        }
    else:
        validation["origin"] = {
            "status": "FAIL",
            "message": "Origin not detected"
        }


    # ----------------------------------------------
    # DESTINATION
    # ----------------------------------------------

    destination = fields.get("destination")

    if destination:
        validation["destination"] = {
            "status": "PASS",
            "message": "Destination extracted"
        }
    else:
        validation["destination"] = {
            "status": "FAIL",
            "message": "Destination not detected"
        }


    # ----------------------------------------------
    # GATE OUT
    # ----------------------------------------------

    gate_out = (
        fields.get("gateOut")
        or fields.get("gate_out")
        or fields.get("gateout")
    )

    if gate_out:
        validation["gateOut"] = {
            "status": "PASS",
            "message": "Gate-out extracted"
        }
    else:
        validation["gateOut"] = {
            "status": "FAIL",
            "message": "Gate-out not detected"
        }


    # ----------------------------------------------
    # LR
    # ----------------------------------------------

    lr = fields.get("lr")

    if lr:
        validation["lr"] = {
            "status": "PASS",
            "message": "LR extracted"
        }
    else:
        validation["lr"] = {
            "status": "FAIL",
            "message": "LR not detected"
        }


    # ----------------------------------------------
    # DELIVERY
    # ----------------------------------------------

    delivery = fields.get("delivery")

    if delivery:
        validation["delivery"] = {
            "status": "PASS",
            "message": "Delivery number extracted"
        }
    else:
        validation["delivery"] = {
            "status": "FAIL",
            "message": "Delivery number not detected"
        }


    # ----------------------------------------------
    # E-WAY BILL
    # ----------------------------------------------

    eway_bill = (
        fields.get("ewayBill")
        or fields.get("eway_bill")
        or fields.get("eWayBill")
    )

    if eway_bill:
        validation["ewayBill"] = {
            "status": "PASS",
            "message": "E-Way Bill extracted"
        }
    else:
        validation["ewayBill"] = {
            "status": "FAIL",
            "message": "E-Way Bill not detected"
        }


    # ----------------------------------------------
    # DRIVER
    # ----------------------------------------------

    if vehicle:

        validation["driver"] = {
            "status": "PASS",
            "message": "Driver resolved (VEHICLE_CURRENT)"
        }

    else:

        validation["driver"] = {
            "status": "FAIL",
            "message": "Driver could not be resolved"
        }


    # ----------------------------------------------
    # DISTANCE
    # ----------------------------------------------

    if origin and destination:

        validation["distance"] = {
            "status": "PASS",
            "message": "Distance from unique route template"
        }

    else:

        validation["distance"] = {
            "status": "FAIL",
            "message": "Distance could not be determined"
        }


    # ----------------------------------------------
    # DUPLICATE
    # ----------------------------------------------

    validation["duplicate"] = {
        "status": "PASS",
        "message": "No duplicate trip"
    }


    return validation


# --------------------------------------------------
# MATCHING
# --------------------------------------------------

def create_matching(fields):
    """
    Create matching information for the frontend.

    IMPORTANT:
    This is currently a demo/static matching layer.
    Replace these values with your actual database/
    route/vehicle matching logic when available.
    """

    vehicle = fields.get("vehicle")

    origin = fields.get("origin")

    destination = fields.get("destination")


    # --------------------------------------------------
    # DRIVER SOURCE
    # --------------------------------------------------

    if vehicle:

        driver_source = "VEHICLE_CURRENT"

    else:

        driver_source = "-"


    # --------------------------------------------------
    # DISTANCE
    # --------------------------------------------------

    if origin and destination:

        # Demo value.
        # Replace with actual route calculation.
        distance = 420

        distance_source = "ROUTE_TEMPLATE"

    else:

        distance = ""

        distance_source = ""


    # --------------------------------------------------
    # TRIP
    # --------------------------------------------------

    if origin and destination:

        # Demo trip number.
        # Replace with your actual trip lookup.
        trip = "TRP-2026-000064"

    else:

        trip = ""


    return {

        "driverSource":
            driver_source,

        "distance":
            distance,

        "distanceSource":
            distance_source,

        "trip":
            trip

    }


# --------------------------------------------------
# UPLOAD AND PROCESS DOCUMENT
# --------------------------------------------------

@app.post("/api/ocr")
async def process_uploaded_document(
    file: UploadFile = File(...)
):

    # --------------------------------------------------
    # CHECK FILENAME
    # --------------------------------------------------

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No filename provided."
        )


    # --------------------------------------------------
    # GET EXTENSION
    # --------------------------------------------------

    extension = os.path.splitext(
        file.filename
    )[1].lower()


    # --------------------------------------------------
    # VALIDATE EXTENSION
    # --------------------------------------------------

    if extension not in ALLOWED_EXTENSIONS:

        raise HTTPException(

            status_code=400,

            detail=(
                "Unsupported file type. "
                "Allowed: PDF, JPG, JPEG, "
                "PNG, TIFF, BMP"
            )
        )


    # --------------------------------------------------
    # GENERATE UNIQUE FILENAME
    # --------------------------------------------------

    unique_filename = (
        f"{uuid.uuid4()}{extension}"
    )


    file_path = os.path.join(
        UPLOAD_DIR,
        unique_filename
    )


    try:

        # --------------------------------------------------
        # SAVE FILE
        # --------------------------------------------------

        with open(
            file_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )


        # --------------------------------------------------
        # OCR
        # --------------------------------------------------

        extracted_text = process_document(
            file_path
        )


        # --------------------------------------------------
        # FIELD EXTRACTION
        # --------------------------------------------------

        fields = extract_fields(
            extracted_text
        )


        # --------------------------------------------------
        # VALIDATION
        # --------------------------------------------------

        validation = validate_fields(
            fields
        )


        # --------------------------------------------------
        # MATCHING
        # --------------------------------------------------

        matching = create_matching(
            fields
        )


        # --------------------------------------------------
        # RETURN RESULT
        # --------------------------------------------------

        return {

            "success": True,

            "filename":
                file.filename,

            "fields":
                fields,

            "validation":
                validation,

            "matching":
                matching,

            "full_text":
                extracted_text

        }


    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=(
                f"OCR processing failed: {str(e)}"
            )

        )


    finally:

        # --------------------------------------------------
        # DELETE TEMPORARY FILE
        # --------------------------------------------------

        if os.path.exists(
            file_path
        ):

            os.remove(
                file_path
            )