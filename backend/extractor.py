import re


# ==========================================================
# CLEAN TEXT
# ==========================================================

def clean_text(text):
    """
    Clean OCR output while keeping useful line structure.
    """

    if not text:
        return ""

    lines = text.splitlines()

    cleaned_lines = []

    for line in lines:

        line = line.strip()

        # Normalize repeated spaces
        line = re.sub(r"[ \t]+", " ", line)

        if line:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


# ==========================================================
# NORMALIZE OCR VALUE
# ==========================================================

def normalize_value(value):

    if not value:
        return None

    value = value.strip()

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value.strip()


# ==========================================================
# FIND VALUE AFTER LABEL
# ==========================================================

def find_value(text, labels):

    for label in labels:

        pattern = (
            rf"(?:^|\n)\s*"
            rf"{label}"
            rf"\s*[:#\-]?\s*"
            rf"([^\n]+)"
        )

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            value = normalize_value(
                match.group(1)
            )

            if value:
                return value

    return None


# ==========================================================
# FIND VALUE ANYWHERE AFTER LABEL
# ==========================================================

def find_value_anywhere(text, labels):

    for label in labels:

        pattern = (
            rf"{label}"
            rf"\s*[:#\-]?\s*"
            rf"([A-Za-z0-9][^\n]*)"
        )

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            value = normalize_value(
                match.group(1)
            )

            if value:
                return value

    return None


# ==========================================================
# VEHICLE
# ==========================================================

def extract_vehicle(text):

    labels = [
        r"vehicle\s*(?:no|number|#)?",
        r"vehicle\s*registration",
        r"registration\s*(?:no|number)?",
        r"reg(?:istration)?\s*(?:no|number)?",
        r"truck\s*(?:no|number)?",
        r"truck"
    ]

    value = find_value(
        text,
        labels
    )

    if value:
        return value

    # Common Indian vehicle-number pattern
    pattern = (
        r"\b[A-Z]{2}"
        r"[\s\-]?"
        r"\d{1,2}"
        r"[\s\-]?"
        r"[A-Z]{1,3}"
        r"[\s\-]?"
        r"\d{3,4}\b"
    )

    match = re.search(
        pattern,
        text.upper()
    )

    if match:
        return match.group(0)

    return None


# ==========================================================
# CUSTOMER
# ==========================================================

def extract_customer(text):

    labels = [
        r"customer\s*name",
        r"customer",
        r"consignee\s*name",
        r"consignee",
        r"client\s*name",
        r"client",
        r"party\s*name",
        r"party"
    ]

    return find_value(
        text,
        labels
    )


# ==========================================================
# LR NUMBER
# ==========================================================

def extract_lr(text):

    labels = [
        r"lr\s*(?:no|number)?",
        r"l\.r\.\s*(?:no|number)?",
        r"lorry\s*receipt\s*(?:no|number)?",
        r"lr"
    ]

    return find_value(
        text,
        labels
    )


# ==========================================================
# DELIVERY
# ==========================================================

def extract_delivery(text):

    labels = [
        r"delivery\s*(?:no|number)?",
        r"delivery\s*number",
        r"delivery",
        r"del\.\s*(?:no|number)?",
        r"delivery\s*document"
    ]

    return find_value(
        text,
        labels
    )


# ==========================================================
# ORIGIN
# ==========================================================

def extract_origin(text):

    labels = [
        r"origin",
        r"source",
        r"from",
        r"dispatch\s*from",
        r"pickup\s*location",
        r"loading\s*location"
    ]

    return find_value(
        text,
        labels
    )


# ==========================================================
# DESTINATION
# ==========================================================

def extract_destination(text):

    labels = [
        r"destination",
        r"to",
        r"consignee\s*location",
        r"delivery\s*location",
        r"unloading\s*location"
    ]

    return find_value(
        text,
        labels
    )


# ==========================================================
# GATE OUT
# ==========================================================

def extract_gate_out(text):

    labels = [
        r"gate[\s\-]*out",
        r"gateout",
        r"gate\s*out\s*time",
        r"gate\s*exit",
        r"gate\s*exit\s*time"
    ]

    value = find_value(
        text,
        labels
    )

    if value:
        return value

    # Date + time fallback
    patterns = [

        r"\b\d{1,2}[./\-]\d{1,2}[./\-]\d{2,4}"
        r"\s+\d{1,2}:\d{2}(?::\d{2})?\b",

        r"\b\d{4}[./\-]\d{1,2}[./\-]\d{1,2}"
        r"\s+\d{1,2}:\d{2}(?::\d{2})?\b",

        r"\b\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4}"
        r"\s+\d{1,2}:\d{2}(?::\d{2})?\b"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return match.group(0)

    return None


# ==========================================================
# WEIGHT
# ==========================================================

def extract_weight(text):

    labels = [
        r"weight",
        r"gross\s*weight",
        r"net\s*weight",
        r"vehicle\s*weight",
        r"weight\s*\(kg\)",
        r"weight\s*kg"
    ]

    value = find_value(
        text,
        labels
    )

    if value:

        match = re.search(
            r"[\d,]+(?:\.\d+)?",
            value
        )

        if match:
            return match.group(0)

    # Weight followed by KG
    pattern = (
        r"\b[\d,]+(?:\.\d+)?\s*kg\b"
    )

    match = re.search(
        pattern,
        text,
        re.IGNORECASE
    )

    if match:

        return re.sub(
            r"\s*kg",
            "",
            match.group(0),
            flags=re.IGNORECASE
        ).strip()

    return None


# ==========================================================
# INVOICE
# ==========================================================

def extract_invoice(text):

    labels = [
        r"invoice\s*(?:no|number|#)?",
        r"invoice"
    ]

    return find_value(
        text,
        labels
    )


# ==========================================================
# E-WAY BILL
# ==========================================================

def extract_eway_bill(text):

    labels = [
        r"e[\s\-]*way\s*bill\s*(?:no|number|#)?",
        r"eway\s*bill\s*(?:no|number|#)?",
        r"e[\s\-]*way\s*(?:no|number)?",
        r"eway"
    ]

    return find_value(
        text,
        labels
    )


# ==========================================================
# DATE
# ==========================================================

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


# ==========================================================
# PHONE
# ==========================================================

def extract_phone(text):

    pattern = (
        r"(?:\+91[\s-]?)?"
        r"[6-9]\d{9}"
    )

    match = re.search(
        pattern,
        text
    )

    if match:
        return match.group(0)

    return None


# ==========================================================
# EMAIL
# ==========================================================

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


# ==========================================================
# AMOUNT
# ==========================================================

def extract_amount(text):

    patterns = [

        r"(?:₹|Rs\.?|INR)"
        r"\s*[\d,]+(?:\.\d{1,2})?",

        r"(?:Total|Amount|Grand Total)"
        r"\s*[:\-]?\s*"
        r"(?:₹|Rs\.?|INR)?"
        r"\s*[\d,]+(?:\.\d{1,2})?"
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


# ==========================================================
# DOCUMENT NUMBER
# ==========================================================

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


# ==========================================================
# NAME
# ==========================================================

def extract_name(text):

    labels = [

        r"customer\s*name",

        r"client\s*name",

        r"consignee\s*name",

        r"consignor\s*name",

        r"name"
    ]

    return find_value(
        text,
        labels
    )


# ==========================================================
# COMPANY
# ==========================================================

def extract_company(text):
    """
    Extract company/organization name.

    Priority:
    1. Consignor Name
    2. Consignor
    3. Company Name
    4. Company
    5. Business Name
    6. Organization
    7. Shipper Name
    8. Shipper

    Avoids returning OCR noise such as:
    Page 1
    Page 2
    Page 1 of 3
    etc.
    """

    # ------------------------------------------------------
    # IMPORTANT:
    # Consignor Name is checked FIRST.
    # For your document:
    #
    # Consignor Name: Tata Steel
    #
    # company = Tata Steel
    # ------------------------------------------------------

    priority_labels = [

        r"consignor\s*name",

        r"consignor",

        r"company\s*name",

        r"company",

        r"business\s*name",

        r"organization\s*name",

        r"organisation\s*name",

        r"organization",

        r"organisation",

        r"shipper\s*name",

        r"shipper",

        r"seller\s*name",

        r"seller"
    ]

    # ------------------------------------------------------
    # FIRST PASS:
    # Look for values on the same line as the label.
    # ------------------------------------------------------

    company = find_value(
        text,
        priority_labels
    )

    if company and not is_invalid_company_value(company):
        return company

    # ------------------------------------------------------
    # SECOND PASS:
    # Sometimes OCR puts the value on the next line.
    #
    # Example:
    #
    # Consignor Name:
    # Tata Steel
    #
    # ------------------------------------------------------

    lines = text.splitlines()

    for index, line in enumerate(lines):

        normalized_line = line.strip()

        for label in priority_labels:

            label_pattern = (
                rf"^\s*{label}"
                rf"\s*[:#\-]?\s*$"
            )

            if re.match(
                label_pattern,
                normalized_line,
                re.IGNORECASE
            ):

                # Check next few lines
                for next_index in range(
                    index + 1,
                    min(index + 3, len(lines))
                ):

                    candidate = normalize_value(
                        lines[next_index]
                    )

                    if (
                        candidate
                        and not is_invalid_company_value(
                            candidate
                        )
                    ):

                        return candidate

    # ------------------------------------------------------
    # DO NOT blindly return the first OCR line.
    #
    # The old code was doing:
    #
    # return line
    #
    # which could return "Page 1".
    # ------------------------------------------------------

    return None


# ==========================================================
# INVALID COMPANY VALUE CHECK
# ==========================================================

def is_invalid_company_value(value):

    if not value:
        return True

    value = normalize_value(value)

    if not value:
        return True

    lower_value = value.lower()

    # ------------------------------------------------------
    # Page numbers
    # ------------------------------------------------------

    page_patterns = [

        r"^page\s*\d+$",

        r"^page\s*\d+\s*of\s*\d+$",

        r"^p\.?\s*\d+$",

        r"^\d+\s*/\s*\d+$"
    ]

    for pattern in page_patterns:

        if re.match(
            pattern,
            lower_value,
            re.IGNORECASE
        ):
            return True

    # ------------------------------------------------------
    # Common OCR metadata
    # ------------------------------------------------------

    invalid_values = {

        "page",

        "page no",

        "page number",

        "document",

        "document page",

        "continued",

        "total",

        "date",

        "name",

        "company",

        "company name",

        "consignor",

        "consignor name",

        "shipper",

        "shipper name"
    }

    if lower_value in invalid_values:
        return True

    return False


# ==========================================================
# DOCUMENT TYPE
# ==========================================================

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


# ==========================================================
# EXTRACT ALL FIELDS
# ==========================================================

def extract_fields(text):

    cleaned = clean_text(text)

    fields = {

        # --------------------------------------------------
        # Logistics fields
        # --------------------------------------------------

        "vehicle":
            extract_vehicle(cleaned),

        "customer":
            extract_customer(cleaned),

        "lr":
            extract_lr(cleaned),

        "delivery":
            extract_delivery(cleaned),

        "origin":
            extract_origin(cleaned),

        "destination":
            extract_destination(cleaned),

        "gateOut":
            extract_gate_out(cleaned),

        "weight":
            extract_weight(cleaned),

        "invoice":
            extract_invoice(cleaned),

        "ewayBill":
            extract_eway_bill(cleaned),

        # --------------------------------------------------
        # Generic fields
        # --------------------------------------------------

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

    # ------------------------------------------------------
    # REMOVE EMPTY VALUES
    # ------------------------------------------------------

    fields = {

        key: value

        for key, value in fields.items()

        if value is not None
        and str(value).strip() != ""
    }

    return fields