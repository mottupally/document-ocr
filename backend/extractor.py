import re


# ==========================================================
# CLEAN TEXT
# ==========================================================

def clean_text(text):
    if not text:
        return ""

    lines = []

    for line in text.splitlines():

        line = line.strip()

        # Normalize spaces
        line = re.sub(r"[ \t]+", " ", line)

        if line:
            lines.append(line)

    return "\n".join(lines)


# ==========================================================
# NORMALIZE VALUE
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

    # Remove obvious punctuation at the beginning/end
    value = value.strip(" :-#|")

    if not value:
        return None

    return value


# ==========================================================
# CHECK WHETHER VALUE IS USEFUL
# ==========================================================

def valid_value(value, min_length=2):

    if not value:
        return False

    value = normalize_value(value)

    if not value:
        return False

    if len(value) < min_length:
        return False

    # Reject values consisting almost entirely of punctuation
    alphanumeric_count = sum(
        c.isalnum()
        for c in value
    )

    if alphanumeric_count < 2:
        return False

    return True


# ==========================================================
# FIND VALUE AFTER LABEL
# ==========================================================

def find_value(text, labels):

    lines = text.splitlines()

    for index, line in enumerate(lines):

        line_clean = line.strip()

        for label in labels:

            # ------------------------------------------------
            # Case 1:
            # Label: Value
            # ------------------------------------------------

            pattern = (
                rf"^\s*{label}"
                rf"\s*(?:[:#\-]+)\s*"
                rf"(.+?)\s*$"
            )

            match = re.match(
                pattern,
                line_clean,
                re.IGNORECASE
            )

            if match:

                value = normalize_value(
                    match.group(1)
                )

                if valid_value(value):
                    return value

            # ------------------------------------------------
            # Case 2:
            # Label Value
            # ------------------------------------------------

            pattern = (
                rf"^\s*{label}"
                rf"\s+(.+?)\s*$"
            )

            match = re.match(
                pattern,
                line_clean,
                re.IGNORECASE
            )

            if match:

                value = normalize_value(
                    match.group(1)
                )

                if valid_value(value):

                    # Don't accept another label as value
                    if not looks_like_label(value):
                        return value

        # ----------------------------------------------------
        # Case 3:
        # Label alone -> next line is value
        # ----------------------------------------------------

        for label in labels:

            if re.fullmatch(
                label,
                line_clean,
                re.IGNORECASE
            ):

                if index + 1 < len(lines):

                    next_line = normalize_value(
                        lines[index + 1]
                    )

                    if (
                        valid_value(next_line)
                        and not looks_like_label(next_line)
                    ):
                        return next_line

    return None


# ==========================================================
# LABEL CHECK
# ==========================================================

def looks_like_label(value):

    if not value:
        return False

    labels = [
        "vehicle",
        "vehicle no",
        "vehicle number",
        "customer",
        "customer name",
        "consignee",
        "consignor",
        "origin",
        "source",
        "destination",
        "from",
        "to",
        "lr",
        "lr no",
        "delivery",
        "gate out",
        "weight",
        "invoice",
        "invoice no",
        "amount",
        "date",
        "name",
        "company",
        "phone",
        "email",
        "eway",
        "e-way bill"
    ]

    return value.strip().lower() in labels


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
        r"lorry\s*(?:no|number)?"
    ]

    value = find_value(
        text,
        labels
    )

    if value:

        # Only accept something that looks like a
        # vehicle registration number
        cleaned = re.sub(
            r"[^A-Za-z0-9]",
            "",
            value.upper()
        )

        pattern = (
            r"^[A-Z]{2}"
            r"\d{1,2}"
            r"[A-Z]{1,3}"
            r"\d{3,4}$"
        )

        if re.match(
            pattern,
            cleaned
        ):
            return value

    # Fallback search
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
        r"consignee\s*name",
        r"consignee",
        r"client\s*name",
        r"party\s*name"
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
        r"l\.r\.\s*(?:no|number)?",
        r"lr\s*(?:no|number|#)",
        r"lorry\s*receipt\s*(?:no|number)?"
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
        r"delivery\s*(?:no|number|#)",
        r"delivery\s*document",
        r"del\.\s*(?:no|number)"
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
        r"dispatch\s*from",
        r"pickup\s*location",
        r"loading\s*location",
        r"consignor\s*location"
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
        r"gate\s*exit",
        r"gate\s*exit\s*time"
    ]

    return find_value(
        text,
        labels
    )


# ==========================================================
# WEIGHT
# ==========================================================

def extract_weight(text):

    labels = [
        r"gross\s*weight",
        r"net\s*weight",
        r"weight",
        r"vehicle\s*weight"
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

    return None


# ==========================================================
# INVOICE
# ==========================================================

def extract_invoice(text):

    labels = [
        r"invoice\s*(?:no|number|#)"
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
        r"eway\s*bill\s*(?:no|number|#)?"
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
import re


def clean_amount(value):

    if not value:
        return ""

    value = value.strip()

    # Remove currency symbols
    value = re.sub(
        r'[₹$€£]',
        '',
        value
    )

    # Find an actual numeric amount
    match = re.search(
        r'\b\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?\b|\b\d+(?:\.\d{1,2})?\b',
        value
    )

    if not match:
        return ""

    return match.group(0)


# ==========================================================
# DOCUMENT NUMBER
# ==========================================================

def extract_document_number(text):

    labels = [
        r"invoice\s*(?:no|number|#)",
        r"receipt\s*(?:no|number|#)",
        r"bill\s*(?:no|number|#)",
        r"slip\s*(?:no|number|#)",
        r"reference\s*(?:no|number|#)",
        r"ref\s*(?:no|number|#)"
    ]

    return find_value(
        text,
        labels
    )


# ==========================================================
# NAME
# ==========================================================

def extract_name(text):

    labels = [
        r"customer\s*name",
        r"client\s*name",
        r"consignee\s*name",
        r"consignor\s*name"
    ]

    return find_value(
        text,
        labels
    )


# ==========================================================
# COMPANY
# ==========================================================

def extract_company(text):

    labels = [
        r"company\s*name",
        r"business\s*name",
        r"organization\s*name",
        r"organisation\s*name",
        r"consignor\s*name",
        r"shipper\s*name",
        r"seller\s*name"
    ]

    value = find_value(
        text,
        labels
    )

    if value:
        return value

    # Do NOT guess a company from random OCR text.
    return None


# ==========================================================
# DOCUMENT TYPE
# ==========================================================

def detect_document_type(text):

    lower_text = text.lower()

    scores = {
        "Invoice": 0,
        "Receipt": 0,
        "Bill": 0,
        "Salary Document": 0,
        "Certificate": 0,
        "Statement": 0,
        "Business Slip": 0,
        "Advertisement / Brochure": 0,
        "Fleet Management Document": 0
    }

    # Invoice
    invoice_patterns = [
        r"\btax\s+invoice\b",
        r"\binvoice\s+(?:no|number)\b",
        r"\binvoice\s*#",
        r"\bsubtotal\b",
        r"\bgrand\s+total\b",
        r"\bgst(?:in)?\b",
        r"\bhsn\b"
    ]

    for pattern in invoice_patterns:

        if re.search(
            pattern,
            lower_text
        ):
            scores["Invoice"] += 2

    # Receipt
    receipt_patterns = [
        r"\breceipt\s+(?:no|number)\b",
        r"\bpayment\s+received\b",
        r"\bpaid\b"
    ]

    for pattern in receipt_patterns:

        if re.search(
            pattern,
            lower_text
        ):
            scores["Receipt"] += 2

    # Bill
    if re.search(
        r"\bbill\s+(?:no|number)\b",
        lower_text
    ):
        scores["Bill"] += 2

    # Salary
    if re.search(
        r"\bsalary\b|\bpayslip\b|\bpay\s+slip\b",
        lower_text
    ):
        scores["Salary Document"] += 5

    # Certificate
    if re.search(
        r"\bcertificate\b|\bcertified\b",
        lower_text
    ):
        scores["Certificate"] += 5

    # Statement
    if re.search(
        r"\baccount\s+statement\b|\bstatement\b",
        lower_text
    ):
        scores["Statement"] += 4

    # Fleet
    fleet_patterns = [
        r"\bfleet\s+management\b",
        r"\bvehicle\s+management\b",
        r"\btrip[\s-]*level\b",
        r"\bdiesel\s+theft\b",
        r"\btyre\s+exchange\b",
        r"\bmoveos\b"
    ]

    fleet_hits = sum(
        bool(re.search(
            pattern,
            lower_text
        ))
        for pattern in fleet_patterns
    )

    if fleet_hits >= 2:

        scores[
            "Fleet Management Document"
        ] += fleet_hits * 2

    best_type = max(
        scores,
        key=scores.get
    )

    # Require a meaningful score
    if scores[best_type] < 2:
        return "Business Document"

    return best_type


# ==========================================================
# WEBSITE
# ==========================================================

def extract_website(text):

    pattern = (
        r"\b(?:https?://)?"
        r"(?:www\.)?"
        r"[A-Za-z0-9][A-Za-z0-9.-]*"
        r"\.[A-Za-z]{2,}"
    )

    matches = re.findall(
        pattern,
        text
    )

    for value in matches:

        value = value.strip(
            ".,;:()[]{}"
        )

        if "." in value:
            return value

    return None


# ==========================================================
# EXTRACT ALL FIELDS
# ==========================================================

def extract_fields(text):

    cleaned = clean_text(
        text
    )

    if not cleaned:
        return {}

    document_type = detect_document_type(
        cleaned
    )

    fields = {
        "document_type": document_type,
        "company": extract_company(cleaned),
        "name": extract_name(cleaned),
        "document_number": extract_document_number(cleaned),
        "date": extract_date(cleaned),
        "amount": extract_amount(cleaned),
        "phone": extract_phone(cleaned),
        "email": extract_email(cleaned)
    }

    # ------------------------------------------------------
    # Logistics fields
    # ------------------------------------------------------

    logistics_signal = re.search(
        r"\bvehicle\b|"
        r"\btruck\b|"
        r"\blorry\b|"
        r"\blr\b|"
        r"\bconsignor\b|"
        r"\bconsignee\b|"
        r"\borigin\b|"
        r"\bdestination\b|"
        r"\bgate[\s-]*out\b|"
        r"\be[\s-]*way\b|"
        r"\bdelivery\b|"
        r"\bdispatch\b|"
        r"\bweight\b",
        cleaned,
        re.IGNORECASE
    )

    if logistics_signal:

        fields.update({
            "vehicle": extract_vehicle(cleaned),
            "customer": extract_customer(cleaned),
            "lr": extract_lr(cleaned),
            "delivery": extract_delivery(cleaned),
            "origin": extract_origin(cleaned),
            "destination": extract_destination(cleaned),
            "gateOut": extract_gate_out(cleaned),
            "weight": extract_weight(cleaned),
            "invoice": extract_invoice(cleaned),
            "ewayBill": extract_eway_bill(cleaned)
        })

    # ------------------------------------------------------
    # Remove empty fields
    # ------------------------------------------------------

    return {
        key: value
        for key, value in fields.items()
        if value is not None
        and str(value).strip() != ""
    }