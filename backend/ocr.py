import os
import cv2
import numpy as np
import pytesseract
import fitz


# ============================================================
# TESSERACT CONFIGURATION
# ============================================================

if os.name == "nt":

    TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    if os.path.exists(TESSERACT_PATH):
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

else:

    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"


# ============================================================
# PREPROCESS IMAGE
# ============================================================

def preprocess_image(image):

    if image is None:
        raise ValueError("Invalid image.")

    # Convert to grayscale
    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    # --------------------------------------------------------
    # Resize image
    # --------------------------------------------------------

    height, width = gray.shape

    target_width = 1800

    if width < target_width:

        scale = target_width / width

        gray = cv2.resize(
            gray,
            None,
            fx=scale,
            fy=scale,
            interpolation=cv2.INTER_CUBIC
        )

    # --------------------------------------------------------
    # Mild contrast enhancement
    # --------------------------------------------------------

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    enhanced = clahe.apply(gray)

    return enhanced


# ============================================================
# THRESHOLD VERSION
# ============================================================

def create_threshold_image(gray):

    threshold = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11
    )

    return threshold


# ============================================================
# DESKEW
# ============================================================

def deskew_image(image):

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    # Use threshold only for detecting text angle
    _, binary = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    coords = np.column_stack(
        np.where(binary > 0)
    )

    if len(coords) < 100:

        return image

    angle = cv2.minAreaRect(coords)[-1]

    if angle < -45:

        angle = -(90 + angle)

    else:

        angle = -angle

    # Ignore unrealistic rotations
    if abs(angle) > 10:

        return image

    height, width = image.shape[:2]

    center = (
        width // 2,
        height // 2
    )

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


# ============================================================
# OCR QUALITY CHECK
# ============================================================

def ocr_score(text):

    if not text:
        return 0

    # Remove whitespace
    characters = [
        c for c in text
        if not c.isspace()
    ]

    if not characters:
        return 0

    # Number of useful alphanumeric characters
    useful = sum(
        c.isalnum()
        for c in characters
    )

    # Number of lines containing text
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    score = (
        useful
        + (len(lines) * 10)
    )

    return score


# ============================================================
# OCR IMAGE
# ============================================================

def extract_text_from_image(image):

    if image is None:

        raise ValueError(
            "Invalid image."
        )

    # --------------------------------------------------------
    # Deskew first
    # --------------------------------------------------------

    image = deskew_image(image)

    # --------------------------------------------------------
    # Preprocess
    # --------------------------------------------------------

    processed = preprocess_image(
        image
    )

    # --------------------------------------------------------
    # Create second OCR version
    # --------------------------------------------------------

    threshold = create_threshold_image(
        processed
    )

    # --------------------------------------------------------
    # OCR VERSION 1
    # --------------------------------------------------------

    text_normal = pytesseract.image_to_string(
        processed,
        config="--oem 3 --psm 6"
    )

    # --------------------------------------------------------
    # OCR VERSION 2
    # --------------------------------------------------------

    text_threshold = pytesseract.image_to_string(
        threshold,
        config="--oem 3 --psm 6"
    )

    # --------------------------------------------------------
    # OCR VERSION 3
    # --------------------------------------------------------

    text_auto = pytesseract.image_to_string(
        processed,
        config="--oem 3 --psm 3"
    )

    # --------------------------------------------------------
    # Select best OCR result
    # --------------------------------------------------------

    results = [
        text_normal,
        text_threshold,
        text_auto
    ]

    best_text = max(
        results,
        key=ocr_score
    )

    return best_text.strip()


# ============================================================
# PROCESS IMAGE
# ============================================================

def process_image(file_path):

    image = cv2.imread(
        file_path
    )

    if image is None:

        raise ValueError(
            "Unable to read image file."
        )

    return extract_text_from_image(
        image
    )


# ============================================================
# PROCESS PDF
# ============================================================

def process_pdf(file_path):

    document = fitz.open(
        file_path
    )

    all_text = []

    try:

        for page_number in range(
            len(document)
        ):

            page = document[
                page_number
            ]

            # Render PDF at higher resolution
            pixmap = page.get_pixmap(
                matrix=fitz.Matrix(3, 3),
                alpha=False
            )

            image_bytes = pixmap.tobytes(
                "png"
            )

            image_array = np.frombuffer(
                image_bytes,
                dtype=np.uint8
            )

            image = cv2.imdecode(
                image_array,
                cv2.IMREAD_COLOR
            )

            if image is None:
                continue

            text = extract_text_from_image(
                image
            )

            all_text.append(
                f"--- Page {page_number + 1} ---\n{text}"
            )

    finally:

        document.close()

    return "\n\n".join(
        all_text
    )


# ============================================================
# MAIN PROCESSOR
# ============================================================

def process_document(file_path):

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

        return process_image(
            file_path
        )

    elif extension == ".pdf":

        return process_pdf(
            file_path
        )

    else:

        raise ValueError(
            f"Unsupported file type: {extension}"
        )