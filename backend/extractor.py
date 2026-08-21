import re


# --------------------------------------------------
# CLEAN TEXT
# --------------------------------------------------

def clean_text(text):
    """
    Clean OCR output.
    """

    lines = text.splitlines()

    cleaned_lines = []

    for line in lines:

        line = line.strip()

        if line:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


# --------------------------------------------------
# FIND VALUE AFTER LABEL
# --------------------------------------------------

def find_value(text, labels):
    """
    Find values after common labels.
    """

    for label in labels:

        pattern = rf"{label}\s*[:\-]?\s*(.+)"

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            value = match.group(1).strip()

            return value

    return None


# --------------------------------------------------
# EXTRACT DATE
# --------------------------------------------------

def extract_date(text):

    patterns = [

        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",

        r"\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b",

        r"\b\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4}\b"

    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text
        )

        if match:
            return match.group(0)

    return None


# --------------------------------------------------
# EXTRACT PHONE NUMBER
# --------------------------------------------------

def extract_phone(text):

    pattern = r"(?:\+91[\s-]?)?[6-9]\d{9}"

    match = re.search(
        pattern,
        text
    )

    if match:
        return match.group(0)

    return None


# --------------------------------------------------
# EXTRACT EMAIL
# --------------------------------------------------

def extract_email(text):

    pattern = (
        r"\b[A-Za-z0-9._%+-]+"
        r"@[A-Za-z0-9.-]+\."
        r"[A-Za-z]{2,}\b"
    )

    match = re.search(
        pattern,
        text
    )

    if match:
        return match.group(0)

    return None


# --------------------------------------------------
# EXTRACT AMOUNT
# --------------------------------------------------

def extract_amount(text):

    patterns = [

        r"(?:₹|Rs\.?|INR)\s*[\d,]+(?:\.\d{1,2})?",

        r"(?:Total|Amount|Grand Total)\s*[:\-]?\s*(?:₹|Rs\.?|INR)?\s*[\d,]+(?:\.\d{1,2})?"

    ]

    for pattern in patterns:

        matches = re.findall(
            pattern,
            text,
            re.IGNORECASE
        )

        if matches:

            return matches[-1].strip()

    return None


# --------------------------------------------------
# EXTRACT INVOICE / RECEIPT NUMBER
# --------------------------------------------------

def extract_document_number(text):

    labels = [

        r"invoice\s*(?:no|number)",

        r"receipt\s*(?:no|number)",

        r"bill\s*(?:no|number)",

        r"slip\s*(?:no|number)",

        r"reference\s*(?:no|number)",

        r"ref\s*(?:no|number)"

    ]

    for label in labels:

        pattern = (
            rf"{label}"
            rf"\s*[:#\-]?\s*"
            rf"([A-Za-z0-9\/\-_]+)"
        )

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            return match.group(1)

    return None


# --------------------------------------------------
# EXTRACT NAME
# --------------------------------------------------

def extract_name(text):

    labels = [

        r"name",

        r"customer\s*name",

        r"customer",

        r"client\s*name",

        r"client"

    ]

    return find_value(
        text,
        labels
    )


# --------------------------------------------------
# EXTRACT COMPANY
# --------------------------------------------------

def extract_company(text):

    labels = [

        r"company",

        r"company\s*name",

        r"business\s*name",

        r"organization",

        r"organisation"

    ]

    company = find_value(
        text,
        labels
    )

    if company:
        return company

    # If no explicit company label exists,
    # use the first meaningful OCR line.

    lines = text.splitlines()

    for line in lines:

        line = line.strip()

        if len(line) > 3:

            if not re.match(
                r"^(date|name|amount|total|invoice|receipt)",
                line,
                re.IGNORECASE
            ):

                return line

    return None


# --------------------------------------------------
# DOCUMENT TYPE
# --------------------------------------------------

def detect_document_type(text):

    lower_text = text.lower()

    if "invoice" in lower_text:
        return "Invoice"

    if "receipt" in lower_text:
        return "Receipt"

    if "bill" in lower_text:
        return "Bill"

    if "salary" in lower_text:
        return "Salary Document"

    if "certificate" in lower_text:
        return "Certificate"

    if "statement" in lower_text:
        return "Statement"

    if "slip" in lower_text:
        return "Business Slip"

    return "Business Document"


# --------------------------------------------------
# EXTRACT ALL FIELDS
# --------------------------------------------------

def extract_fields(text):

    cleaned = clean_text(text)

    fields = {

        "document_type":
            detect_document_type(cleaned),

        "company":
            extract_company(cleaned),

        "name":
            extract_name(cleaned),

        "document_number":
            extract_document_number(cleaned),

        "date":
            extract_date(cleaned),

        "amount":
            extract_amount(cleaned),

        "phone":
            extract_phone(cleaned),

        "email":
            extract_email(cleaned)

    }

    # Remove fields that weren't detected
    fields = {
        key: value
        for key, value in fields.items()
        if value
    }

    return fields