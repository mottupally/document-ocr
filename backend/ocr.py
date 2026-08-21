import os
import cv2
import numpy as np
import pytesseract
import fitz

from PIL import Image


# --------------------------------------------------
# TESSERACT CONFIGURATION
# --------------------------------------------------

TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

if os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


# --------------------------------------------------
# IMAGE PREPROCESSING
# --------------------------------------------------

def preprocess_image(image):
    """
    Improve image quality before OCR.
    """

    # Convert BGR to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Remove noise
    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    # Improve contrast using OTSU thresholding
    _, threshold = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    return threshold


# --------------------------------------------------
# DESKEW IMAGE
# --------------------------------------------------

def deskew_image(image):
    """
    Correct small rotation/tilt in the document.
    """

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Threshold
    _, binary = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    coords = np.column_stack(np.where(binary > 0))

    if len(coords) < 100:
        return image

    angle = cv2.minAreaRect(coords)[-1]

    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    # Ignore extremely large/incorrect angles
    if abs(angle) > 15:
        return image

    height, width = image.shape[:2]

    center = (width // 2, height // 2)

    matrix = cv2.getRotationMatrix2D(
        center,
        angle,
        1.0
    )

    rotated = cv2.warpAffine(
        image,
        matrix,
        (width, height),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE
    )

    return rotated


# --------------------------------------------------
# OCR IMAGE
# --------------------------------------------------

def extract_text_from_image(image):
    """
    Perform OCR on an image.
    """

    # Deskew
    image = deskew_image(image)

    # Preprocess
    processed = preprocess_image(image)

    # OCR
    text = pytesseract.image_to_string(
        processed,
        config="--psm 6"
    )

    return text


# --------------------------------------------------
# PROCESS IMAGE FILE
# --------------------------------------------------

def process_image(file_path):
    """
    Read an image and extract text.
    """

    image = cv2.imread(file_path)

    if image is None:
        raise ValueError("Unable to read image file.")

    text = extract_text_from_image(image)

    return text


# --------------------------------------------------
# PROCESS PDF
# --------------------------------------------------

def process_pdf(file_path):
    """
    Convert each PDF page to an image and perform OCR.
    """

    document = fitz.open(file_path)

    all_text = []

    for page_number in range(len(document)):

        page = document[page_number]

        pixmap = page.get_pixmap(
            matrix=fitz.Matrix(2, 2)
        )

        image_bytes = pixmap.tobytes("png")

        image_array = np.frombuffer(
            image_bytes,
            dtype=np.uint8
        )

        image = cv2.imdecode(
            image_array,
            cv2.IMREAD_COLOR
        )

        text = extract_text_from_image(image)

        all_text.append(
            f"--- Page {page_number + 1} ---\n{text}"
        )

    document.close()

    return "\n\n".join(all_text)


# --------------------------------------------------
# MAIN FILE PROCESSOR
# --------------------------------------------------

def process_document(file_path):
    """
    Detect file type and perform OCR.
    """

    extension = os.path.splitext(
        file_path
    )[1].lower()

    image_extensions = [
        ".jpg",
        ".jpeg",
        ".png",
        ".tif",
        ".tiff",
        ".bmp"
    ]

    if extension in image_extensions:

        return process_image(file_path)

    elif extension == ".pdf":

        return process_pdf(file_path)

    else:

        raise ValueError(
            f"Unsupported file type: {extension}"
        )