import os
import cv2
import numpy as np
import pytesseract
import fitz


# ============================================================
# TESSERACT CONFIGURATION
# ============================================================

if os.name == "nt":

    # Windows
    TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    if os.path.exists(TESSERACT_PATH):
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

else:

    # Render / Linux
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"


# ============================================================
# PREPROCESS IMAGE
# ============================================================

def preprocess_image(image):
    
    if image is None:
        raise ValueError("Invalid image.")

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    height, width = gray.shape

    # Reduce large phone images
    target_width = 1000

    if width > target_width:

        scale = target_width / width

        gray = cv2.resize(
            gray,
            None,
            fx=scale,
            fy=scale,
            interpolation=cv2.INTER_AREA
        )

    return gray

    # Mild contrast enhancement
    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    enhanced = clahe.apply(gray)

    return enhanced

    # --------------------------------------------------------
    # Resize only when necessary
    # --------------------------------------------------------

    if width != target_width:
    
       scale = target_width / width

    gray = cv2.resize(
        gray,
        None,
        fx=scale,
        fy=scale,
        interpolation=(
            cv2.INTER_AREA
            if width > target_width
            else cv2.INTER_CUBIC
        )
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
# DESKEW
# ============================================================

def deskew_image(image):

    if image is None:
        return image

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    # Small processing only for angle detection
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

    angle = cv2.minAreaRect(
        coords
    )[-1]

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
# OCR QUALITY SCORE
# ============================================================

def ocr_score(text):

    if not text:
        return 0

    characters = [
        c for c in text
        if not c.isspace()
    ]

    if not characters:
        return 0

    useful = sum(
        c.isalnum()
        for c in characters
    )

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    return useful + (len(lines) * 10)


# ============================================================
# OCR IMAGE
# ============================================================
import time

def extract_text_from_image(image):

    if image is None:
        raise ValueError("Invalid image.")

    start = time.time()

    print("OCR: original image size:",
          image.shape[1],
          "x",
          image.shape[0])

    processed = preprocess_image(image)

    print("OCR: processed image size:",
          processed.shape[1],
          "x",
          processed.shape[0])

    print("OCR: starting Tesseract...")

    try:

        text = pytesseract.image_to_string(
            processed,
            config="--oem 3 --psm 6",
            timeout=60
        )

    except RuntimeError as e:

        print(
            "OCR: Tesseract failed after",
            round(time.time() - start, 2),
            "seconds"
        )

        raise RuntimeError(
            f"Tesseract OCR timed out or failed: {str(e)}"
        )

    print(
        "OCR: completed in",
        round(time.time() - start, 2),
        "seconds"
    )

    return text.strip()
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

            # ------------------------------------------------
            # Render PDF at moderate resolution
            # ------------------------------------------------

            pixmap = page.get_pixmap(
                matrix=fitz.Matrix(2, 2),
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